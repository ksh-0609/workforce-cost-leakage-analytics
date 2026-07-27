from db_connection import get_engine
import pandas as pd
import random
from datetime import timedelta
from sqlalchemy import text

random.seed(44)

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

CREEP_EMPLOYEE_RATE = 0.12
CREEP_SHIFT_PROBABILITY = 0.75
CREEP_MINUTES_RANGE = (5, 20)
MISSED_BREAK_HOUR_THRESHOLD = 6
MISSED_BREAK_RATE = 0.15
NATURAL_NOISE_MINUTES = 2

employee_ids = shifts_df["employee_id"].unique().tolist()
num_creep_employees = max(1, int(len(employee_ids) * CREEP_EMPLOYEE_RATE))
creep_employees = set(random.sample(employee_ids, num_creep_employees))

punches = []
ground_truth_rows = []

for _, shift in shifts_df.iterrows():
    employee_id = int(shift["employee_id"])
    scheduled_start = shift["scheduled_start"]
    scheduled_end = shift["scheduled_end"]
    shift_hours = (scheduled_end - scheduled_start).total_seconds() / 3600.0

    natural_in_jitter = random.randint(
        -NATURAL_NOISE_MINUTES,
        NATURAL_NOISE_MINUTES
    )

    natural_out_jitter = random.randint(
        -NATURAL_NOISE_MINUTES,
        NATURAL_NOISE_MINUTES
    )

    clock_in = scheduled_start + timedelta(minutes=natural_in_jitter)
    clock_out = scheduled_end + timedelta(minutes=natural_out_jitter)

    if (
        employee_id in creep_employees
        and random.random() < CREEP_SHIFT_PROBABILITY
    ):
        early_in = random.randint(*CREEP_MINUTES_RANGE)
        late_out = random.randint(*CREEP_MINUTES_RANGE)

        clock_in -= timedelta(minutes=early_in)
        clock_out += timedelta(minutes=late_out)

        ground_truth_rows.append({
            "employee_id": employee_id,
            "label_date": shift["shift_date"],
            "anomaly_type": "overtime_creep",
            "injected": True
        })

    break_taken = True

    if (
        shift_hours > MISSED_BREAK_HOUR_THRESHOLD
        and random.random() < MISSED_BREAK_RATE
    ):
        break_taken = False

        ground_truth_rows.append({
            "employee_id": employee_id,
            "label_date": shift["shift_date"],
            "anomaly_type": "missed_break",
            "injected": True
        })

    punches.append({
        "shift_id": int(shift["shift_id"]),
        "employee_id": employee_id,
        "clock_in": clock_in,
        "clock_out": clock_out,
        "break_taken": break_taken
    })

punches_df = pd.DataFrame(punches)

punches_df.to_sql(
    "time_clock_punches",
    engine,
    if_exists="append",
    index=False
)

ground_truth_df = pd.DataFrame(ground_truth_rows)

ground_truth_df.to_sql(
    "ground_truth_labels",
    engine,
    if_exists="append",
    index=False
)

creep_count = len(
    ground_truth_df[
        ground_truth_df["anomaly_type"] == "overtime_creep"
    ]
)

break_count = len(
    ground_truth_df[
        ground_truth_df["anomaly_type"] == "missed_break"
    ]
)

print(f"Inserted {len(punches_df)} punches.")
print(
    f"Injected {creep_count} overtime-creep instances across "
    f"{len(creep_employees)} employees."
)
print(f"Injected {break_count} missed-break instances.")