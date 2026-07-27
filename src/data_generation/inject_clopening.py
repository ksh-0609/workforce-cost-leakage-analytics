from db_connection import get_engine
import pandas as pd
import random
from datetime import datetime, time
from sqlalchemy import text

random.seed(43)

engine = get_engine()

with engine.connect() as conn:
    shifts_df = pd.read_sql(
        text("""
            SELECT shift_id, employee_id, shift_date
            FROM shifts_scheduled
            ORDER BY employee_id, shift_date
        """),
        conn
    )

CLOPENING_EMPLOYEE_RATE = 0.08
INSTANCES_PER_EMPLOYEE_RANGE = (3, 6)

employee_ids = shifts_df["employee_id"].unique().tolist()
num_selected = max(1, int(len(employee_ids) * CLOPENING_EMPLOYEE_RATE))
clopening_employees = random.sample(employee_ids, num_selected)

ground_truth_rows = []
schedule_updates = []

for emp_id in clopening_employees:
    emp_shifts = shifts_df[
        shifts_df["employee_id"] == emp_id
    ].reset_index(drop=True)

    eligible_pair_indexes = []

    for i in range(len(emp_shifts) - 1):
        gap_days = (
            emp_shifts.loc[i + 1, "shift_date"]
            - emp_shifts.loc[i, "shift_date"]
        ).days

        if gap_days == 1:
            eligible_pair_indexes.append(i)

    if not eligible_pair_indexes:
        continue

    n_instances = min(
        random.randint(*INSTANCES_PER_EMPLOYEE_RANGE),
        len(eligible_pair_indexes)
    )

    chosen_indexes = random.sample(
        eligible_pair_indexes,
        n_instances
    )

    for i in chosen_indexes:
        closing_shift = emp_shifts.loc[i]
        opening_shift = emp_shifts.loc[i + 1]

        new_close_end = datetime.combine(
            closing_shift["shift_date"],
            time(22, 0)
        )

        new_open_start = datetime.combine(
            opening_shift["shift_date"],
            time(7, 0)
        )

        schedule_updates.append(
            (
                int(closing_shift["shift_id"]),
                "scheduled_end",
                new_close_end
            )
        )

        schedule_updates.append(
            (
                int(opening_shift["shift_id"]),
                "scheduled_start",
                new_open_start
            )
        )

        ground_truth_rows.append({
            "employee_id": int(emp_id),
            "label_date": closing_shift["shift_date"],
            "anomaly_type": "clopening",
            "injected": True
        })

with engine.begin() as connection:
    for shift_id, column_name, new_value in schedule_updates:
        query = text(
            f"""
            UPDATE shifts_scheduled
            SET {column_name} = :new_value
            WHERE shift_id = :shift_id
            """
        )

        connection.execute(
            query,
            {
                "new_value": new_value,
                "shift_id": shift_id
            }
        )

ground_truth_df = pd.DataFrame(ground_truth_rows)

ground_truth_df.to_sql(
    "ground_truth_labels",
    engine,
    if_exists="append",
    index=False
)

print(
    f"Injected {len(ground_truth_df)} clopening instances across "
    f"{len(clopening_employees)} employees."
)