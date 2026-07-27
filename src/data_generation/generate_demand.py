from db_connection import get_engine
import pandas as pd
import numpy as np
from sqlalchemy import text
from datetime import date, timedelta

np.random.seed(42)

engine = get_engine()

with engine.connect() as conn:
    locations_df = pd.read_sql(
        text("SELECT location_id FROM locations"),
        conn
    )

    departments_df = pd.read_sql(
        text("SELECT department_id, name FROM departments"),
        conn
    )

start_date = date(2026, 1, 1)
end_date = date(2026, 6, 30)

STORE_OPEN_HOUR = 8
STORE_CLOSE_HOUR = 22

# A few known dates where demand genuinely spikes (sale events)
HOLIDAY_SPIKES = {
    date(2026, 1, 26),
    date(2026, 3, 8),
    date(2026, 4, 14),
    date(2026, 6, 21)
}

# How strongly each department's workload scales with overall store footfall
DEPARTMENT_MULTIPLIER = {
    "Sales Floor": 1.0,
    "Cash Counter": 0.9,
    "Customer Service": 0.5,
    "Stockroom": 0.3,
    "Management": 0.2
}

def hourly_base_curve(hour):
    # A rough retail-shaped day: quiet morning, lunch bump, evening peak
    curve = {
        8: 20,
        9: 30,
        10: 45,
        11: 60,
        12: 85,
        13: 90,
        14: 70,
        15: 65,
        16: 75,
        17: 90,
        18: 100,
        19: 95,
        20: 80,
        21: 50
    }
    return curve.get(hour, 20)

records = []
current_date = start_date

while current_date <= end_date:
    is_weekend = current_date.weekday() in (5, 6)
    weekend_multiplier = 1.4 if is_weekend else 1.0
    holiday_multiplier = 1.8 if current_date in HOLIDAY_SPIKES else 1.0

    for _, loc in locations_df.iterrows():
        for _, dept in departments_df.iterrows():
            dept_multiplier = DEPARTMENT_MULTIPLIER[dept["name"]]

            for hour in range(STORE_OPEN_HOUR, STORE_CLOSE_HOUR):
                base = hourly_base_curve(hour)
                noise = np.random.normal(loc=1.0, scale=0.12)

                demand_value = max(
                    0,
                    round(
                        base
                        * weekend_multiplier
                        * holiday_multiplier
                        * dept_multiplier
                        * noise,
                        2
                    )
                )

                records.append({
                    "location_id": int(loc["location_id"]),
                    "department_id": int(dept["department_id"]),
                    "demand_date": current_date,
                    "hour_of_day": hour,
                    "demand_value": demand_value
                })

    current_date += timedelta(days=1)

demand_df = pd.DataFrame(records)

demand_df.to_sql(
    "demand_hourly",
    engine,
    if_exists="append",
    index=False
)

print(f"Inserted {len(demand_df)} hourly demand rows.")