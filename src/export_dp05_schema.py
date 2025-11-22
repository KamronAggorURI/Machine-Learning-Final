r"""Export DP05 (census tract demographic) table schema to a CSV reference file.

Usage:
  python src\export_dp05_schema.py

Output:
  outputs\tables\dp05_cols.csv - Two-column CSV with column_name and data_type
"""
import os
from pathlib import Path
from google.cloud import bigquery

# Set credentials
creds_path = Path(__file__).parent.parent / "credentials" / "machine-learning-final-477822-031ba3aac2f9.json"
if creds_path.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_path)
else:
    raise FileNotFoundError(f"Credentials file not found at {creds_path}")

client = bigquery.Client(project="machine-learning-final-477822")

# Get schema from the census tract table (DP05 equivalent)
table = client.get_table("bigquery-public-data.census_bureau_acs.censustract_2020_5yr")

# Extract column names and data types
schema_data = []
for field in table.schema:
    schema_data.append({
        'column_name': field.name,
        'data_type': field.field_type
    })

# Write to CSV
import pandas as pd
df = pd.DataFrame(schema_data)
output_path = Path(__file__).parent.parent / "outputs" / "tables" / "dp05_cols.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False)

print(f"Schema exported to {output_path}")
print(f"Total columns: {len(df)}")
print("\nFirst 10 columns:")
print(df.head(10).to_string(index=False))
