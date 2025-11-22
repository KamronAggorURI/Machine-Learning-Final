r"""Utility to extract DP03 demographic variables from the public ACS dataset
and save them either as a table in your GCP project or as a local CSV for quick reference.

Usage examples (from the workspace root):
  # write RI tract DP03 variables to a BigQuery table
  python src\load_DP03.py --state-fips 44 --bq-dataset ml_final --bq-table DP03_ri --write-bq

  # write RI tract DP03 variables to a local CSV
  python src\load_DP03.py --state-fips 44 --local-csv outputs\tables\DP03_ri.csv

The script will attempt to auto-detect a DP03 table in the
`bigquery-public-data.census_bureau_acs` dataset; you can override it with --table-name.
"""
import argparse
import os
from pathlib import Path
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

# Ensure credentials are set before importing BigQuery client
creds_path = Path(__file__).parent.parent / "credentials" / "machine-learning-final-477822-031ba3aac2f9.json"
if creds_path.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_path)
else:
    raise FileNotFoundError(f"Credentials file not found at {creds_path}")


def ensure_dataset(client, dataset_id, location="US"):
    try:
        ds = client.get_dataset(dataset_id)
        print(f"Dataset {dataset_id} already exists")
    except NotFound:
        print(f"Creating dataset {dataset_id} in project {client.project}")
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = location
        client.create_dataset(dataset)
        print("Created dataset")


def find_DP03_table(client, candidate=None):
    public = "bigquery-public-data.census_bureau_acs"
    if candidate:
        # check existence
        try:
            client.get_table(f"{public}.{candidate}")
            return candidate
        except Exception:
            print(f"Table {candidate} not found in {public}")
    # fallback: look for censustract table (contains demographic data equivalent to DP03)
    print("No explicit DP03 table name provided; searching for census tract demographic tables...")
    sql = """
    SELECT table_name
    FROM `bigquery-public-data.census_bureau_acs.INFORMATION_SCHEMA.TABLES`
    WHERE LOWER(table_name) LIKE '%censustract%'
    ORDER BY table_name DESC
    """
    rows = client.query(sql).result()
    names = [r.table_name for r in rows]
    if not names:
        raise RuntimeError("No DP03-like or census tract table found in the public ACS dataset")
    print("Found candidate tables:", names)
    # prefer the most recent 5-year estimate
    selected = names[0]
    print(f"Using table: {selected}")
    return selected


def get_DP03_columns(client, table_name):
    """Extract key demographic columns from the census tract table.
    
    Instead of pulling all 245 columns (which can be slow), we select
    the most useful demographic indicators that align with DP03 concepts.
    """
    # Key demographic variables to extract (commonly used in analysis)
    key_columns = [
        'geo_id',
        'total_pop',
        'median_age',
        'male_pop',
        'female_pop',
        'white_pop',
        'black_pop',
        'hispanic_pop',
        'asian_pop',
        'american_indian_pop',
        'bachelor_degree',
        'graduate_professional_degree',
        'less_than_high_school_graduate',
        'median_income',
        'poverty',
        'unemployed_pop',
        'civilian_labor_force',
        'occupied_housing_units',
        'owner_occupied_housing_units',
        'housing_units_renter_occupied',
        'vacant_housing_units',
        'median_rent',
        'median_year_structure_built',
        'gini_index',
    ]
    
    # Query actual schema to see which of these exist
    sql = f"""
    SELECT column_name
    FROM `bigquery-public-data.census_bureau_acs.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = '{table_name}'
    ORDER BY ordinal_position
    """
    df = client.query(sql).result().to_dataframe()
    available = set(df['column_name'].tolist())
    
    # Filter to only columns that exist
    cols = [c for c in key_columns if c in available]
    print(f"Extracted {len(cols)} key demographic columns")
    return cols


def build_query(public_table, columns, state_fips=None):
    cols = ',\n  '.join(columns)
    where = ""
    if state_fips:
        where = f"WHERE geo_id LIKE '{state_fips}%'"
    sql = f"""
    SELECT
      {cols}
    FROM `{public_table}`
    {where}
    """
    return sql


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state-fips', default=None, help='State FIPS prefix to filter geo_id (e.g., 44 for RI)')
    parser.add_argument('--table-name', default=None, help='Exact DP03 table name if known')
    parser.add_argument('--write-bq', action='store_true', help='Write the result to a BigQuery table in your project')
    parser.add_argument('--bq-dataset', default='ml_final', help='Destination dataset in your project')
    parser.add_argument('--bq-table', default='DP03_ri', help='Destination table name in your project')
    parser.add_argument('--local-csv', default=None, help='If provided, also write a local CSV to this path')
    args = parser.parse_args()

    client = bigquery.Client()
    public_prefix = 'bigquery-public-data.census_bureau_acs'

    DP03_table = find_DP03_table(client, args.table_name)
    public_table = f"{public_prefix}.{DP03_table}"
    print('Using public table:', public_table)

    cols = get_DP03_columns(client, DP03_table)
    if not cols:
        raise RuntimeError('No DP03 columns found')
    print('Selected columns count:', len(cols))

    query = build_query(public_table, cols, state_fips=args.state_fips)
    print('Running query...')

    if args.write_bq:
        dataset_id = f"{client.project}.{args.bq_dataset}"
        ensure_dataset(client, dataset_id)
        destination = f"{client.project}.{args.bq_dataset}.{args.bq_table}"
        job_config = bigquery.QueryJobConfig(destination=destination, write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
        job = client.query(query, job_config=job_config)
        job.result()
        print(f'Wrote results to {destination}')
        # load into dataframe for optional CSV
        df = client.list_rows(destination).to_dataframe()
    else:
        # run query and fetch results locally
        job = client.query(query)
        df = job.result().to_dataframe()

    if args.local_csv:
        outdir = os.path.dirname(args.local_csv)
        if outdir and not os.path.exists(outdir):
            os.makedirs(outdir)
        df.to_csv(args.local_csv, index=False)
        print('Wrote local CSV to', args.local_csv)

    print('Rows retrieved:', len(df))


if __name__ == '__main__':
    main()
