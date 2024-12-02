-- models/final/final_booking_analytics.sql
SELECT
    hotel,
    arrival_date_year,
    arrival_date_month,
    total_bookings,
    revenue,
    avg_lead_time
FROM {{ ref('trn_booking_metrics') }}
ORDER BY arrival_date_year, arrival_date_month
