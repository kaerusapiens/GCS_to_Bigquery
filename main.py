import csv
from google.cloud import storage
from google.cloud import bigquery
import os


def download_csv_from_storage(bucket_name, file_name):
    """Downloads a CSV file from Cloud Storage."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    data = blob.download_as_string()
    return data

def parse_csv_data(data):
    """Parses CSV data into a list of dictionaries."""

    # Decode data if it is in bytes
    decoded_data = data.decode('utf-8') if isinstance(data, bytes) else data
    rows = []
    reader = csv.DictReader(decoded_data.splitlines())
    for row in reader:
        rows.append(row)
    return rows

def load_data_to_bigquery(rows, dataset_name, table_name):
    """Loads parsed CSV data into a BigQuery table."""

    bigquery_client = bigquery.Client()
    table_ref = bigquery_client.dataset(dataset_name).table(table_name)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,  # Specify JSON format
        autodetect=True,  # Automatically detect the schema
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Replace table data
    )

    load_job = bigquery_client.load_table_from_json(
        rows, table_ref, job_config=job_config
    )
    load_job.result()  # Wait for the job to complete

    # Check for errors
    if load_job.errors:
        return load_job.errors
    return []

def main(event,context):
    """
    Triggered by a file upload to Cloud Storage.
    Processes the CSV file and loads it into a BigQuery table.
    """

    file_name = event['name']
    dataset_id = os.environ.get('dataset_id')
    bucket_id = os.environ.get('bucket_id')
    table_name = file_name.split('.', 1)[0]  # Sanitize table name
    # Download the CSV file
    data = download_csv_from_storage(bucket_id, file_name)

    # Parse the CSV data
    rows = parse_csv_data(data)

    # Load the data into BigQuery
    errors = load_data_to_bigquery(rows,dataset_id , table_name)

    # Check for errors
    if errors == []:
        print(f"CSV file '{file_name}' successfully loaded into BigQuery.")
    else:
        print(f"Errors occurred while loading CSV file '{file_name}' into BigQuery.")

if __name__ == "__main__":
    main()