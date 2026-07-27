DROP VIEW IF EXISTS v_clopening_flags;

   CREATE VIEW v_clopening_flags AS
   WITH ordered_shifts AS (
       SELECT
           employee_id, shift_date, scheduled_start, scheduled_end,
           LEAD(scheduled_start) OVER (PARTITION BY employee_id ORDER BY shift_date) AS next_shift_start
       FROM shifts_scheduled
   )
   SELECT
       employee_id, shift_date, scheduled_end, next_shift_start,
       EXTRACT(EPOCH FROM (next_shift_start - scheduled_end)) / 3600.0 AS rest_gap_hours
   FROM ordered_shifts
   WHERE next_shift_start IS NOT NULL
     AND EXTRACT(EPOCH FROM (next_shift_start - scheduled_end)) / 3600.0 < 10;