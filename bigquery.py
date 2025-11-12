from google.cloud import bigquery
import pandas as pd
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/callummagarian/Desktop/Machine-Learning-Final/credentials/machine-learning-final-477822-031ba3aac2f9.json"
# big query library
client = bigquery.Client()
# make a wrapper around DP05 table to get demographic data
query = """
SELECT
  geo_id,
  total_pop,
  male_pop,
  female_pop,
  white_pop,
  black_pop,
  asian_pop,
  hispanic_pop,
  amerindian_pop,
  other_race_pop,
  two_or_more_races_pop,
  not_hispanic_pop
FROM
  `bigquery-public-data.census_bureau_acs.censustract_2014_5yr`
-- WHERE geo_id LIKE '44007%'
"""

job = client.query(query)
rows = list(job.result())
df = pd.DataFrame([dict(row) for row in rows])
print(df.head())7

df.to_csv('census_tract_2014_demographic.csv', index=False)