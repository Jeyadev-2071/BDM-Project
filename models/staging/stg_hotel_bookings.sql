
SELECT
    hotel,
    is_canceled,
    lead_time,
    arrival_date_year,
    arrival_date_month,
    CAST(adults AS INT64) + CAST(children AS INT64) + CAST(babies AS INT64) AS total_guests,
    CAST(stays_in_weekend_nights AS INT64) + CAST(stays_in_week_nights AS INT64) AS stay_duration,
    adr,
    reservation_status,
    reservation_status_date
FROM {{ source('BDM_PROJECT', 'CURATED_HOTEL_DATA') }}