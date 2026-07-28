DROP VIEW IF EXISTS v_staffing_ratio;

   CREATE VIEW v_staffing_ratio AS
   WITH shift_hour_buckets AS (
       SELECT
           s.shift_id,
           e.location_id,
           e.department_id,
           s.shift_date,
           EXTRACT(HOUR FROM bucket_hour)::int AS hour_of_day,
           EXTRACT(EPOCH FROM (
               LEAST(s.scheduled_end, bucket_hour + interval '1 hour')
               - GREATEST(s.scheduled_start, bucket_hour)
           )) / 3600.0 AS hours_in_bucket
       FROM shifts_scheduled s
       JOIN employees e ON e.employee_id = s.employee_id
       CROSS JOIN LATERAL generate_series(
           date_trunc('hour', s.scheduled_start),
           date_trunc('hour', s.scheduled_end - interval '1 second'),
           interval '1 hour'
       ) AS bucket_hour
   ),
   scheduled_labor_by_hour AS (
       SELECT location_id, department_id, shift_date, hour_of_day,
              SUM(hours_in_bucket) AS scheduled_labor_hours
       FROM shift_hour_buckets
       GROUP BY location_id, department_id, shift_date, hour_of_day
   )
   -- SERVICE_RATE_PER_STAFF_HOUR = 20: one staff-hour is assumed to adequately
   -- serve ~20 units of hourly demand. In a real business this comes from
   -- historical throughput data; here it's a documented modeling assumption.
   SELECT
       d.location_id, d.department_id, d.demand_date, d.hour_of_day, d.demand_value,
       ROUND((d.demand_value / 20.0)::numeric, 2) AS ideal_labor_hours,
       COALESCE(sl.scheduled_labor_hours, 0) AS scheduled_labor_hours,
       CASE WHEN (d.demand_value / 20.0) = 0 THEN NULL
            ELSE ROUND((COALESCE(sl.scheduled_labor_hours, 0) / (d.demand_value / 20.0))::numeric, 3)
       END AS staffing_ratio
   FROM demand_hourly d
   LEFT JOIN scheduled_labor_by_hour sl
       ON sl.location_id = d.location_id AND sl.department_id = d.department_id
       AND sl.shift_date = d.demand_date AND sl.hour_of_day = d.hour_of_day;