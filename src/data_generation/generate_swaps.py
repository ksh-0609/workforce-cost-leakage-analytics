from db_connection import get_engine
import pandas as pd
import numpy as np
import random
from datetime import timedelta
from sqlalchemy import text

random.seed(45)
np.random.seed(45)

engine = get_engine()

with engine.connect() as conn:
    shifts_df = pd.read_sql(
        text("""
            SELECT shift_id,
                   employee_id,
                   shift_date,
                   scheduled_start,
                   scheduled_end
            FROM shifts_scheduled
        """),
        conn
    )

    employees_df = pd.read_sql(
        text("""
            SELECT employee_id,
                   location_id
            FROM employees
        """),
        conn
    )

    existing_labels_df = pd.read_sql(
        text("""
            SELECT employee_id,
                   label_date
            FROM ground_truth_labels
            WHERE anomaly_type IN ('overtime_creep', 'missed_break')
        """),
        conn
    )

existing_labels_set = set(
    zip(
        existing_labels_df["employee_id"],
        existing_labels_df["label_date"]
    )
)

eligible_shifts = shifts_df[
    ~shifts_df.apply(
        lambda r: (
            r["employee_id"],
            r["shift_date"]
        ) in existing_labels_set,
        axis=1
    )
].reset_index(drop=True)

SWAP_RATE = 0.05
num_swaps = int(len(eligible_shifts) * SWAP_RATE)
swap_candidate_shifts = eligible_shifts.sample(n=num_swaps)

swaps = []
ground_truth_rows = []
punch_reassignments = []

for _, shift in swap_candidate_shifts.iterrows():

    original_employee_id = int(shift["employee_id"])

    original_location_id = int(
        employees_df.loc[
            employees_df["employee_id"] == original_employee_id,
            "location_id"
        ].iloc[0]
    )

    same_location_employees = employees_df[
        (employees_df["location_id"] == original_location_id)
        &
        (employees_df["employee_id"] != original_employee_id)
    ]

    covering_employee_id = int(
        same_location_employees.sample(1).iloc[0]["employee_id"]
    )

    shift_hours = (
        shift["scheduled_end"] - shift["scheduled_start"]
    ).total_seconds() / 3600.0

    shift_week_start = (
        shift["shift_date"]
        - timedelta(days=int(shift["shift_date"].weekday()))
    )

    shift_week_end = shift_week_start + timedelta(days=6)

    covering_shifts_that_week = shifts_df[
        (shifts_df["employee_id"] == covering_employee_id)
        &
        (shifts_df["shift_date"] >= shift_week_start)
        &
        (shifts_df["shift_date"] <= shift_week_end)
        &
        (shifts_df["shift_id"] != shift["shift_id"])
    ]

    covering_other_hours = (
        (
            covering_shifts_that_week["scheduled_end"]
            - covering_shifts_that_week["scheduled_start"]
        ).dt.total_seconds() / 3600.0
    ).sum()

    caused_overtime = (
        covering_other_hours + shift_hours
    ) > 40

    swap_date = (
        shift["shift_date"]
        - timedelta(days=random.randint(1, 5))
    )

    manager_approved = bool(random.random() < 0.75)

    swaps.append({
        "original_employee_id": original_employee_id,
        "covering_employee_id": covering_employee_id,
        "shift_id": int(shift["shift_id"]),
        "swap_date": swap_date,
        "manager_approved": manager_approved
    })

    punch_reassignments.append(
        (
            int(shift["shift_id"]),
            covering_employee_id
        )
    )

    if caused_overtime:
        ground_truth_rows.append({
            "employee_id": covering_employee_id,
            "label_date": shift["shift_date"],
            "anomaly_type": "swap_overtime",
            "injected": True
        })

swaps_df = pd.DataFrame(swaps)

swaps_df.to_sql(
    "shift_swaps",
    engine,
    if_exists="append",
    index=False
)

with engine.begin() as connection:
    for shift_id, covering_employee_id in punch_reassignments:
        connection.execute(
            text("""
                UPDATE time_clock_punches
                SET employee_id = :covering_employee_id
                WHERE shift_id = :shift_id
            """),
            {
                "covering_employee_id": covering_employee_id,
                "shift_id": shift_id
            }
        )

if ground_truth_rows:
    pd.DataFrame(ground_truth_rows).to_sql(
        "ground_truth_labels",
        engine,
        if_exists="append",
        index=False
    )

print(f"Inserted {len(swaps_df)} shift swaps.")
print(
    f"Reassigned {len(punch_reassignments)} punch records "
    f"to their covering employee."
)
print(
    f"Of those, {len(ground_truth_rows)} swaps pushed "
    f"the covering employee into overtime."
)