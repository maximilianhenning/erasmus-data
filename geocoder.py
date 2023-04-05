import pandas as pd
from os import path
import re
from unidecode import unidecode

dir = path.dirname(__file__)
geocode_df = pd.read_csv(path.join(dir, "geocode.csv"), sep = ";", encoding = "utf-8")
institutions_df = pd.read_csv(path.join(dir, "institutions.csv"), sep = ";", encoding = "utf-8")

geocoded_dict = {}
to_be_coded_raw = institutions_df["City"].tolist()
for city in to_be_coded_raw:
    city_raw = city
    city = re.sub(r"\(.*?\)", "", city)
    city = city.lower()
    city = city.strip()
    city = city.replace("  ", " ")
    city = unidecode(city)
    for x in range(0, 10):
        city = city.strip(" " + str(x))
    if city not in geocoded_dict.keys():
        geocoded_dict[city] = [city, city_raw]

geocode_df = geocode_df.loc[geocode_df["Country Code"].isin(["PT", "ES", "AD", "FR", "IT", "CH",
                                                             "BE", "LU", "NL", "GB", "IE", "LI",
                                                             "DE", "DK", "NO", "SE", "FI", "EE",
                                                             "LV", "LT", "BY", "RU", "UA", "PL",
                                                             "CZ", "SK", "AT", "HU", "RO", "BG",
                                                             "GR", "TR", "SI", "HR", "BA", "MK",
                                                             "RS", "AL", "MT"
                                                             ])]
geocode_df = geocode_df[["Name", "Coordinates"]]
geocode_df["name_code"] = geocode_df["Name"].str.lower().apply(unidecode)

city_counter = 0
coded_counter = 0
for city in geocoded_dict.keys():
    city_counter += 1
    if city in geocode_df["name_code"].tolist():
        coded_counter += 1
        geocoded_dict[city].append(geocode_df.loc[geocode_df["name_code"] == city]["Coordinates"].values[0].split(", ")[0])
        geocoded_dict[city].append(geocode_df.loc[geocode_df["name_code"] == city]["Coordinates"].values[0].split(", ")[1])
        print("Done:", str((city_counter / len(geocoded_dict.keys()))*100)[:5] + "% - Coded:", str((coded_counter / len(geocoded_dict.keys()))*100)[:5] + "%")
geocoded_df = pd.DataFrame.from_dict(geocoded_dict, orient = "index")
geocoded_df = geocoded_df.reset_index().drop(columns = "index").rename(columns = {0: "name_code", 1: "name_full", 2: "lat", 3: "lon"})
pd.DataFrame.to_csv(geocoded_df, path.join(dir, "geocoded.csv"), encoding = "utf-8", sep = ";")