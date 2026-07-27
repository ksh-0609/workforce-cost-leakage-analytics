DROP VIEW IF EXISTS v_missed_breaks;

   CREATE VIEW v_missed_breaks AS
   SELECT
       p.employee_id,
       p.clock_in::date AS shift_date,
       EXTRACT(EPOCH FROM (p.clock_out - p.clock_in)) / 3600.0 AS shift_length_hours,
       p.break_taken
   FROM time_clock_punches p
   WHERE EXTRACT(EPOCH FROM (p.clock_out - p.clock_in)) / 3600.0 > 6
     AND p.break_taken = FALSE;