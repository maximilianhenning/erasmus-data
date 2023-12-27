Dependencies:

1. pandas
2. os
3. glob
4. re
5. unidecode

Data:

1. Erasmus exchanges: European Commission
- [2008](https://web.archive.org/web/20181228150816/https://data.europa.eu/euodp/repository/ec/dg-eac/erasmus-data-2008-2009/student_data_2008.csv)
- [2009](https://web.archive.org/web/20181002153331/https://data.europa.eu/euodp/repository/ec/dg-eac/erasmus-data-2009-2010/student_data_2009.csv)
- [2010](https://web.archive.org/web/20181002153553/https://data.europa.eu/euodp/repository/ec/dg-eac/erasmus-data-2010-2011/student_data_2010.csv)
- [2011](https://data.europa.eu/euodp/en/data/storage/f/2015-03-13T153634/student_1112.csv)
- [2012](https://web.archive.org/web/20181002153620/http://data.europa.eu/euodp/data/uploads/EAC/SM_2012_13_20141103_01.csv)
- [2013](https://web.archive.org/web/20181002153523/https://data.europa.eu/euodp/repository/ec/dg-eac/erasmus-data-2013-2014/Student_Mobility_2013-14.xlsx)
- [2014-2020](https://data.europa.eu/data/datasets/erasmus-mobility-statistics-2014-2020)
2. Geocoding: [Geonames](https://data.opendatasoft.com/explore/dataset/geonames-all-cities-with-a-population-1000%40public/table/?disjunctive.cou_name_en&sort=name)
3. Erasmus institutions: [European Commission](https://erasmus-plus.ec.europa.eu/document/higher-education-institutions-holding-an-eche-2021-2027)

How to use:

1. Clone repository
2. Download the data
3. Create a "data" subfolder, put the exchange files in there. Convert to CSV if necessary and name them according to their year ("2008", "2009", etc.)
4. Create a "geocoding" subfolder, put the files on institutions and geocoding in there and name them "institutions" and "geocode"
5. Run geocoder.py
6. Run wrangler.py
7. Run combiner.py
8. Enjoy your data!

For more information, see my [blog post](https://zarasophos.net/erasmus/).