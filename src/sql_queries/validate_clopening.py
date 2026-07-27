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
    flagged_df = pd.read_sql(
        text("""
            SELECT employee_id, shift_date
            FROM v_clopening_flags
        """),
        conn
    )

    ground_truth_df = pd.read_sql(
        text("""
            SELECT employee_id, label_date
            FROM ground_truth_labels
            WHERE anomaly_type = 'clopening'
        """),
        conn
    )

flagged_pairs = set(
    zip(
        flagged_df["employee_id"],
        flagged_df["shift_date"]
    )
)

known_pairs = set(
    zip(
        ground_truth_df["employee_id"],
        ground_truth_df["label_date"]
    )
)

true_positives = flagged_pairs & known_pairs

recall = (
    len(true_positives) / len(known_pairs)
    if known_pairs
    else 0
)

precision = (
    len(true_positives) / len(flagged_pairs)
    if flagged_pairs
    else 0
)

print(f"Known injected clopening instances: {len(known_pairs)}")
print(f"Flagged by v_clopening_flags:       {len(flagged_pairs)}")
print(f"True positives:                     {len(true_positives)}")
print(f"Recall:    {recall:.1%}")
print(f"Precision: {precision:.1%}")