-- models/transformed/trn_booking_metrics.sql
SELECT
    hotel,
    arrival_date_year,
    arrival_date_month,
    COUNT(*) AS total_bookings,
    SUM(CASE WHEN is_canceled = FALSE THEN adr * stay_duration ELSE 0 END) AS revenue,
    AVG(lead_time) AS avg_lead_time
FROM {{ ref('stg_hotel_bookings') }}
GROUP BY hotel, arrival_date_year, arrival_date_month
