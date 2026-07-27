import sys
import os
from sqlalchemy import text
import pandas as pd

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "data_generation"
    )
)

from db_connection import get_engine

engine = get_engine()

with engine.connect() as conn:
    overtime_df = pd.read_sql(
        text("""
            SELECT employee_id,
                   week_start,
                   overtime_hours
            FROM v_weekly_overtime_cost
            WHERE overtime_hours > 0
        """),
        conn
    )

    ground_truth_df = pd.read_sql(
        text("""
            SELECT employee_id,
                   label_date
            FROM ground_truth_labels
            WHERE anomaly_type = 'swap_overtime'
        """),
        conn
    )

overtime_df["week_start"] = pd.to_datetime(
    overtime_df["week_start"]
).dt.date

flagged_weeks = set(
    zip(
        overtime_df["employee_id"],
        overtime_df["week_start"]
    )
)

ground_truth_df["label_date"] = pd.to_datetime(
    ground_truth_df["label_date"]
)

ground_truth_df["week_start"] = (
    ground_truth_df["label_date"]
    - pd.to_timedelta(
        ground_truth_df["label_date"].dt.weekday,
        unit="D"
    )
).dt.date

known_cause_weeks = set(
    zip(
        ground_truth_df["employee_id"],
        ground_truth_df["week_start"]
    )
)

true_positives = flagged_weeks & known_cause_weeks

recall = (
    len(true_positives) / len(known_cause_weeks)
    if known_cause_weeks
    else 0
)

precision = (
    len(true_positives) / len(flagged_weeks)
    if flagged_weeks
    else 0
)

natural_overtime_weeks = (
    flagged_weeks - known_cause_weeks
)

print(
    f"Employee-weeks with a known swap-driven cause: "
    f"{len(known_cause_weeks)}"
)

print(
    f"Employee-weeks flagged with overtime_hours > 0: "
    f"{len(flagged_weeks)}"
)

print(
    f"Recall (swap-caused weeks correctly flagged): "
    f"{recall:.1%}"
)

print(
    f"Precision (flagged weeks with a known swap cause): "
    f"{precision:.1%}"
)

print(
    f"Flagged weeks with no known swap cause "
    f"(natural scheduling variance): "
    f"{len(natural_overtime_weeks)}"
)