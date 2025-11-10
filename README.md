# Machine-Learning-Final
Kamron Aggor, Callum Magarian, Casandra Frey
---

## Abstract:
H3 is a geospatial indexing system developed and used by Uber that utilizes hierarchical layers of connected hexagons to represent areas in space. H3 differs from traditional indexing methods (e.g. choropleths), in its use of hexagonal indexing system, which offers unique advantages for the analysis of geospatial data due to the fact that hexagons are equidistant to their neighbors in every direction. This is particularly useful for machine learning applications, where non-uniform geometries can introduce compounding amounts of error into a predictive model, and lack stability in matrix operations.
Using this method of indexing, we will be investigating the features that are highly correlated with economic and demographic qualities in the state of Rhode Island, and training a clustering model that hopefully generalizes to other parts of the region, the country, and the world. Spatial distinctiveness is an effective basis for clustering, where training clusters on data in certain areas and then testing on others would demonstrate dynamic socio-economic circumstances. This involves dividing training and testing splits into small geographical units, possibly states or even counties. Clustering techniques such as K-means would learn from economic data, from which we could determine whether clusters could sufficiently outline economic data in other regions.

## Data Description:
CARTO Documentation has an immense amount of geospatial datasets. When browsing through the contents of the repository, there were a series of aforementioned socioeconomic datasets with strong overlap in data quality with no significant issues regarding missing data. One dataset we shall be analyzing - "Selected Economic Characteristics” - demonstrates information about employment status, occupation, income, class, and more. Another is The American Community Survey, which describes demographics and sentiments throughout the United States, as well as up to 5-year projections for this data. 
Methods:
Tools that are in consideration for this project include Google Colab for creating notebooks, data analysis tools, and model training and inference. We plan to gauge both the loss reduction resulting from the translation of non-uniform spatial data to H3, as well as the overall precision of our predictions generated from our machine learning model.

---
Resources:
1. https://clausa.app.carto.com/public/catalog/dataset/acs_dp3economic_5587b4d2 (Selected Economic Characteristics, 5 years estimates - United States of America)

2. https://clausa.app.carto.com/public/catalog/dataset/acs_dp5demograp_87f2e206 (ACS Demographic and Housing Estimates, 5 years estimates)
