Dependencies:

1. pandas
2. os
3. glob
4. re
5. unidecode

Data:

1. Erasmus exchanges: [European Commission](https://data.europa.eu/data/datasets?query=erasmus%20mobility%20statistics&locale=en&publisher=http%3A%2F%2Fpublications.europa.eu%2Fresource%2Fauthority%2Fcorporate-body%2FEAC&page=1&limit=10)
2. Erasmus institutions: [European Commission](https://erasmus-plus.ec.europa.eu/document/higher-education-institutions-holding-an-eche-2021-2027)
3. Geocoding: [Geonames](https://data.opendatasoft.com/explore/dataset/geonames-all-cities-with-a-population-1000%40public/table/?disjunctive.cou_name_en&sort=name)

How to use:

1. Clone repository
2. Download the data
3. Create a "data" subfolder, put the exchange files in there. Convert to CSV if necessary and name them according to their year ("2008", "2009", etc.)
4. Create a "geocoding" subfolder, put the files on institutions and geocoding in there and name them "institutions" and "geocode"
5. Run geocoder.py
6. Run wrangler.py
7. Run combiner.py
8. Enjoy your data!