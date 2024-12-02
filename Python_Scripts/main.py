from google.cloud import bigquery
import pandas as pd

# Initialize BigQuery Client
client = bigquery.Client()

# Function to fetch data from BigQuery
def fetch_data_from_bigquery(project_id, dataset_id, table_id):
    query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_id}`"
    print(f"Fetching data from {project_id}.{dataset_id}.{table_id}...")
    df = client.query(query).to_dataframe()
    print(f"Data fetched: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df

# Function to clean the data
def clean_data(df):
    print("Cleaning data...")

    # 1. Handle missing values
    # Replace 'NA' or empty strings with appropriate defaults
    df['children'] = df['children'].replace(['NA', '', None], 0).astype(float)  # Convert to float to handle decimals
    df['company'] = df['company'].replace(['NA', '', None], 'unknown')
    df['adr'] = df['adr'].replace(['NA', '', None], 0).astype(float)

    # 2. Correct data types
    # Convert numeric columns
    df['is_canceled'] = df['is_canceled'].replace(['NA', '', None], '0').astype(int).astype(bool)
    df['lead_time'] = df['lead_time'].replace(['NA', '', None], 0).astype(int)
    df['adults'] = df['adults'].replace(['NA', '', None], 0).astype(int)
    df['babies'] = df['babies'].replace(['NA', '', None], 0).astype(int)

    # 3. Remove invalid rows (adults + children + babies = 0)
    # Ensure at least one guest exists per booking
    df = df[(df['adults'] + df['children'] + df['babies']) > 0]

    # 4. Handle outliers in 'adr' (e.g., extreme high values)
    # Calculate 99th percentile threshold for adr
    adr_threshold = df['adr'].quantile(0.99)
    df = df[df['adr'] <= adr_threshold]

    # 5. Standardize column strings (e.g., lowercase for string columns)
    # Apply to all string columns
    string_columns = df.select_dtypes(include=['object']).columns
    df[string_columns] = df[string_columns].apply(lambda col: col.str.strip().str.lower())

    print("Cleaning completed.")
    return df


# Function to write data to BigQuery
def write_to_bigquery(df, project_id, dataset_id, table_id):
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    print(f"Writing data to {table_ref}...")

    # Define BigQuery job config
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # Replace the table if it exists
        autodetect=True
    )

    # Load data into BigQuery
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()  # Wait for the job to complete
    print(f"Data written to {table_ref}.")

# Main function
def main():
    # Replace with your GCP project and dataset details
    project_id = "iitj-capstone-project-group-18"
    raw_dataset_id = "BDM_PROJECT"
    curated_dataset_id = "BDM_PROJECT"
    raw_table_id = "RAW_DATA"
    curated_table_id = "CURATED_HOTEL_DATA"

    # Fetch data from RAW_DATA table
    raw_data = fetch_data_from_bigquery(project_id, raw_dataset_id, raw_table_id)

    # Clean the data
    cleaned_data = clean_data(raw_data)

    # Write cleaned data to CURATED_DATA table
    write_to_bigquery(cleaned_data, project_id, curated_dataset_id, curated_table_id)

if __name__ == "__main__":
    main()
