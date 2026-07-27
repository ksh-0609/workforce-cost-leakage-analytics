DROP VIEW IF EXISTS v_weekly_overtime_cost;

   CREATE VIEW v_weekly_overtime_cost AS
   WITH weekly_hours AS (
       SELECT
           p.employee_id,
           DATE_TRUNC('week', p.clock_in) AS week_start,
           SUM(EXTRACT(EPOCH FROM (p.clock_out - p.clock_in)) / 3600.0) AS hours_worked
       FROM time_clock_punches p
       WHERE p.clock_out IS NOT NULL
       GROUP BY p.employee_id, DATE_TRUNC('week', p.clock_in)
   )
   SELECT
       w.employee_id,
       e.full_name,
       e.department_id,
       w.week_start,
       w.hours_worked,
       GREATEST(w.hours_worked - 40, 0) AS overtime_hours,
       GREATEST(w.hours_worked - 40, 0) * e.hourly_rate * 1.5 AS overtime_cost
   FROM weekly_hours w
   JOIN employees e ON e.employee_id = w.employee_id;