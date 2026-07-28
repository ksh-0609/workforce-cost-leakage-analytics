Employee-weeks with a known swap-driven cause: 363
Employee-weeks flagged with overtime_hours > 0: 347
Recall (swap-caused weeks correctly flagged): 84.0%
Precision (flagged weeks with a known swap cause): 87.9%
Flagged weeks with no known swap cause (natural scheduling variance): 42


v_clopening_flags (validated against `clopening`)
Known injected clopening instances: 31
Flagged by v_clopening_flags:       31
True positives:                     31
Recall:    100.0%
Precision: 100.0%


Known injected missed-break instances: 1552
Flagged by v_missed_breaks:            1552
True positives:                        1552
Recall:    100.0%
Precision: 100.0%


## v_staffing_ratio (sanity-checked, not ground-truth-validated)
## v_staffing_ratio (sanity-checked, not ground-truth-validated)

   No injected ground truth exists for over/understaffing — validated instead by
   confirming the view surfaces a mismatch known to be structurally present in the
   data (fixed weekly schedules vs. variable demand).

   Note: the first version of this view divided raw customer-footfall demand
   directly by scheduled labor-hours, producing a meaningless near-zero ratio
   across the board. Fixed by introducing an explicit SERVICE_RATE_PER_STAFF_HOUR
   = 20 conversion (demand units one staff-hour can adequately serve) — the same
   kind of assumption a real business would derive from historical throughput data.

   - Overall avg/min/max staffing ratio: 0.91 / 0.00 / 16.44
   - Overstaffed hours (ratio > 1.2): 16,695 / Understaffed hours (ratio < 0.8): 38,918
   - Weekday avg ratio: 0.98 vs Weekend avg ratio: 0.71 (weekday correctly higher)
   - Jan 19 avg ratio: 1.01 vs Jan 26 (holiday spike) avg ratio: 0.59 (Jan 26 correctly lower)