from google.cloud import bigquery

client = bigquery.Client()

# Define table ID
table_id = "iitj-capstone-project-group-18.BDM_PROJECT.RAW_DATA"
schema = [
    bigquery.SchemaField("hotel", "STRING"),
    bigquery.SchemaField("is_canceled", "BOOLEAN"),
    bigquery.SchemaField("lead_time", "STRING"),
    bigquery.SchemaField("arrival_date_year", "STRING"),
    bigquery.SchemaField("arrival_date_month", "STRING"),
    bigquery.SchemaField("arrival_date_week_number", "STRING"),
    bigquery.SchemaField("arrival_date_day_of_month", "STRING"),
    bigquery.SchemaField("stays_in_weekend_nights", "STRING"),
    bigquery.SchemaField("stays_in_week_nights", "STRING"),
    bigquery.SchemaField("adults", "STRING"),
    bigquery.SchemaField("children", "STRING"),  # To handle "NA" or invalid entries
    bigquery.SchemaField("babies", "STRING"),
    bigquery.SchemaField("meal", "STRING"),
    bigquery.SchemaField("country", "STRING"),
    bigquery.SchemaField("market_segment", "STRING"),
    bigquery.SchemaField("distribution_channel", "STRING"),
    bigquery.SchemaField("is_repeated_guest", "STRING"),
    bigquery.SchemaField("previous_cancellations", "STRING"),
    bigquery.SchemaField("previous_bookings_not_canceled", "STRING"),
    bigquery.SchemaField("reserved_room_type", "STRING"),
    bigquery.SchemaField("assigned_room_type", "STRING"),
    bigquery.SchemaField("booking_changes", "STRING"),
    bigquery.SchemaField("deposit_type", "STRING"),
    bigquery.SchemaField("agent", "STRING"),
    bigquery.SchemaField("company", "STRING"),
    bigquery.SchemaField("days_in_waiting_list", "STRING"),
    bigquery.SchemaField("customer_type", "STRING"),
    bigquery.SchemaField("adr", "STRING"),
    bigquery.SchemaField("required_car_parking_spaces", "STRING"),
    bigquery.SchemaField("total_of_special_requests", "STRING"),
    bigquery.SchemaField("reservation_status", "STRING"),
    bigquery.SchemaField("reservation_status_date", "STRING"),
]
# Job configuration with autodetect for the schema
job_config = bigquery.LoadJobConfig(
    schema=schema,
    autodetect=False, 
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1
)

# Load the CSV file
with open("data\hotel_bookings.csv", "rb") as source_file:
    job = client.load_table_from_file(source_file, table_id, job_config=job_config)

# Wait for the job to complete

job.result()

print(f"Data loaded into {table_id}.")
