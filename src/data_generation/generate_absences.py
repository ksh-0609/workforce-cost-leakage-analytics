from db_connection import get_engine
import pandas as pd
import random
from datetime import date, timedelta
from sqlalchemy import text

random.seed(46)

engine = get_engine()

with engine.connect() as conn:
    employees_df = pd.read_sql(
        text("""
            SELECT employee_id
            FROM employees
        """),
        conn
    )

start_date = date(2026, 1, 1)
end_date = date(2026, 6, 30)
total_days = (end_date - start_date).days + 1

ABSENCES_PER_EMPLOYEE_RANGE = (2, 8)
ABSENCE_TYPES = ["sick", "personal", "emergency"]
ABSENCE_TYPE_WEIGHTS = [0.6, 0.3, 0.1]

absences = []

for _, emp in employees_df.iterrows():
    employee_id = int(emp["employee_id"])

    n_absences = random.randint(
        *ABSENCES_PER_EMPLOYEE_RANGE
    )

    absence_offsets = random.sample(
        range(total_days),
        n_absences
    )

    for offset in absence_offsets:
        absence_date = start_date + timedelta(days=offset)

        absence_type = random.choices(
            ABSENCE_TYPES,
            weights=ABSENCE_TYPE_WEIGHTS,
            k=1
        )[0]

        absences.append({
            "employee_id": employee_id,
            "absence_date": absence_date,
            "absence_type": absence_type
        })

absences_df = pd.DataFrame(absences)

absences_df.to_sql(
    "leave_absences",
    engine,
    if_exists="append",
    index=False
)

print(
    f"Inserted {len(absences_df)} leave/absence records across "
    f"{len(employees_df)} employees."
)

print(absences_df["absence_type"].value_counts())