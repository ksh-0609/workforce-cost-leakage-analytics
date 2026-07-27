import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data_generation"))

from db_connection import get_engine
import pandas as pd

engine = get_engine()

flagged_df = pd.read_sql("SELECT employee_id, shift_date FROM v_missed_breaks", engine)
flagged_pairs = set(zip(flagged_df["employee_id"], flagged_df["shift_date"]))

ground_truth_df = pd.read_sql(
    "SELECT employee_id, label_date FROM ground_truth_labels WHERE anomaly_type = 'missed_break'",
    engine
)
known_pairs = set(zip(ground_truth_df["employee_id"], ground_truth_df["label_date"]))

true_positives = flagged_pairs & known_pairs
recall = len(true_positives) / len(known_pairs) if known_pairs else 0
precision = len(true_positives) / len(flagged_pairs) if flagged_pairs else 0

print(f"Known injected missed-break instances: {len(known_pairs)}")
print(f"Flagged by v_missed_breaks:            {len(flagged_pairs)}")
print(f"True positives:                        {len(true_positives)}")
print(f"Recall:    {recall:.1%}")
print(f"Precision: {precision:.1%}")