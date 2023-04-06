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
geocode_df = geocode_df[["Name", "Coordinates", "Population", "Alternate Names"]]
geocode_df["name_code"] = geocode_df["Name"].str.lower().apply(unidecode)
geocode_df["Alternate Names"] = geocode_df["Alternate Names"].str.lower()

city_counter = 0
success_counter = 0
for city in geocoded_dict.keys():
    city_counter += 1
    # Check in primary name
    if city in geocode_df["name_code"].to_list():
        # Check for potential misattributions to smaller cities (Roma), find those coordinates
        if geocode_df.loc[geocode_df["name_code"] == city]["Population"].values[0] < 5000:
            if geocode_df["Alternate Names"].str.contains("," + str(city) + ",", na = False).any():
                geocoded_dict[city].append(geocode_df.loc[geocode_df["Alternate Names"].str.contains("," + str(city) + ",", na = False)].sort_values("Population")["Coordinates"].values[0].split(", ")[0])
                geocoded_dict[city].append(geocode_df.loc[geocode_df["Alternate Names"].str.contains("," + str(city) + ",", na = False)].sort_values("Population")["Coordinates"].values[0].split(", ")[1])
                success_counter += 1
        # Main coordinate finder
        if len(geocoded_dict[city]) == 2:
                geocoded_dict[city].append(geocode_df.loc[geocode_df["name_code"] == city]["Coordinates"].values[0].split(", ")[0])
                geocoded_dict[city].append(geocode_df.loc[geocode_df["name_code"] == city]["Coordinates"].values[0].split(", ")[1])
                success_counter += 1
    # Otherwise check in alternate names
    elif geocode_df["Alternate Names"].str.contains("," + str(city) + ",", na = False).any():
        geocoded_dict[city].append(geocode_df.loc[geocode_df["Alternate Names"].str.contains("," + str(city) + ",", na = False)].sort_values("Population")["Coordinates"].values[0].split(", ")[0])
        geocoded_dict[city].append(geocode_df.loc[geocode_df["Alternate Names"].str.contains("," + str(city) + ",", na = False)].sort_values("Population")["Coordinates"].values[0].split(", ")[1])
        success_counter += 1
    print("Done:", str((city_counter / len(geocoded_dict.keys()))*100)[:5] + "% - Success:", str((success_counter / len(geocoded_dict.keys()))*100)[:5] + "%")
geocoded_df = pd.DataFrame.from_dict(geocoded_dict, orient = "index")
geocoded_df = geocoded_df.reset_index().drop(columns = [0, "index"]).reset_index().rename(columns = {"index": "id", 1: "name", 2: "lat", 3: "lon"})
geocoded_df = geocoded_df.loc[geocoded_df["lat"].notna()]
pd.DataFrame.to_csv(geocoded_df, path.join(dir, "geocoded.csv"), encoding = "utf-8", sep = ";", index = False)