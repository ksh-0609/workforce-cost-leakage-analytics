from db_connection import get_engine
import pandas as pd
import random
from datetime import date, timedelta, datetime, time

random.seed(42)

engine = get_engine()
employees_df = pd.read_sql("SELECT employee_id FROM employees", engine)

start_date = date(2026, 1, 1)
end_date = date(2026, 6, 30)

STORE_OPEN_HOUR = 8
STORE_CLOSE_HOUR = 22
SHIFT_LENGTHS = [6, 6.5, 7, 7.5, 8]

shifts = []

for _, emp in employees_df.iterrows():
    employee_id = int(emp["employee_id"])

    # Each employee gets a FIXED set of 5 working weekdays for the whole
    # simulation (0=Monday ... 6=Sunday) — so their schedule looks like a
    # real recurring pattern, not random noise every single day.
    working_days = set(random.sample(range(7), 5))

    current_date = start_date

    while current_date <= end_date:

        if current_date.weekday() in working_days:

            shift_length = random.choice(SHIFT_LENGTHS)

            latest_start_hour = int(STORE_CLOSE_HOUR - shift_length)

            possible_start_hours = list(
                range(STORE_OPEN_HOUR, latest_start_hour + 1)
            )

            start_hour = random.choice(possible_start_hours)

            scheduled_start = datetime.combine(
                current_date,
                time(start_hour, 0)
            )

            scheduled_end = scheduled_start + timedelta(hours=shift_length)

            shifts.append({
                "employee_id": employee_id,
                "shift_date": current_date,
                "scheduled_start": scheduled_start,
                "scheduled_end": scheduled_end
            })

        current_date += timedelta(days=1)

shifts_df = pd.DataFrame(shifts)

shifts_df.to_sql(
    "shifts_scheduled",
    engine,
    if_exists="append",
    index=False
)

print(
    f"Inserted {len(shifts_df)} scheduled shifts across {employees_df.shape[0]} employees."
)

print(
    f"Average shifts per employee: {len(shifts_df) / employees_df.shape[0]:.1f}"
)