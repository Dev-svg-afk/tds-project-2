# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "duckdb",
# ]
# ///
import duckdb
import os

s3_bucket_path = 's3://indian-high-court-judgments/metadata/parquet/year=*/court=*/bench=*/metadata.parquet'
output_file_name = 'filtered_judgments_metadata.parquet'

duckdb.sql("INSTALL httpfs; LOAD httpfs; INSTALL parquet; LOAD parquet;")

query = f"""
SELECT court, decision_date, date_of_registration, year
FROM read_parquet('{s3_bucket_path}')
"""

filtered_data = duckdb.query(query).to_df()
filtered_data.to_parquet(output_file_name)