import pandas as pd
from os import path
from glob import glob
import re
from unidecode import unidecode

dir = path.dirname(__file__)
geocode_df = pd.read_csv(path.join(dir, "geocoding", "geocode.csv"), sep = ";", encoding = "utf-8")
institutions_df = pd.read_csv(path.join(dir, "geocoding", "institutions.csv"), sep = ";", encoding = "utf-8")

cities_raw_initial = institutions_df["City"].tolist()
cities_raw_expand = []
data_results = glob(path.join(dir, "data/*"))
for file in data_results:
    year = int(file.split("\\")[-1].split(".")[0])
    if year > 2013:
        if year > 2019:
            df = pd.read_csv(file, sep = ";", encoding = "latin-1")
        else:
            df = pd.read_csv(file, sep = ";", encoding = "utf-8")
        sending_list = df["Sending City"].tolist()
        for city in sending_list:
            cities_raw_expand.append(city)
        receiving_list = df["Receiving City"].tolist()
        for city in receiving_list:
            cities_raw_expand.append(city)
cities_raw_expand = list(set(cities_raw_expand))
cities_raw = cities_raw_initial + cities_raw_expand

def geocoded_dict_creator(cities_list):
    geocoded_dict = {}
    for city_raw in cities_list:
        city = str(city_raw)
        city = re.sub(r"\[.+?\]|\(.+?\)|\{.+?\}", "", city)
        city = re.sub(r"[^a-zA-Z\s]+", "", city)
        city = city.lower().strip().replace("  ", " ")
        city = unidecode(city)
        city_split = [token for token in city.split(" ") if not token.isdigit()]
        city = " ".join(city_split)
        if len(city) > 2 and city not in geocoded_dict.keys():
            geocoded_dict[city] = [city_raw]
    return geocoded_dict
geocoded_dict = geocoded_dict_creator(cities_raw)

geocode_df = geocode_df.loc[geocode_df["Country Code"].isin(["PT", "ES", "FR", "IT", "RS", "MT",
                                                             "BE", "LU", "NL", "GB", "IE", "LI",
                                                             "DE", "DK", "NO", "SE", "FI", "EE",
                                                             "LV", "LT", "PL", "IS", "LI", "MK",
                                                             "CZ", "SK", "AT", "HU", "RO", "BG",
                                                             "GR", "TR", "SI", "HR", "MK",
                                                             ])]
geocode_df = geocode_df[["Name", "Coordinates", "Population", "Alternate Names", "Country Code"]]
geocode_df["name_code"] = geocode_df["Name"].str.lower().apply(unidecode)
geocode_df["Alternate Names"] = geocode_df["Alternate Names"].str.lower()

def geocoded_df_creator(geocoded_dict):
    city_counter = 0
    success_counter = 0
    for city in geocoded_dict.keys():
        city_counter += 1
        search_string = str("," + city + ",")
        # Check in primary name
        if city in geocode_df["name_code"].to_list():
            # Check for potential misattributions to smaller cities (Roma), find those coordinates
            if geocode_df.loc[geocode_df["name_code"] == city]["Population"].values[0] < 5000:
                if geocode_df["Alternate Names"].str.contains(search_string, na = False).any():
                    coordinates = geocode_df.loc[geocode_df["Alternate Names"].str.contains(search_string, na = False)].sort_values("Population")["Coordinates"].values[0].split(", ")
                    geocoded_dict[city].append(coordinates[0])
                    geocoded_dict[city].append(coordinates[1])
                    country_code = geocode_df.loc[geocode_df["Alternate Names"].str.contains(search_string, na = False)].sort_values("Population")["Country Code"].values[0]
                    geocoded_dict[city].append(country_code)
                    success_counter += 1
            # Main coordinate finder
            if len(geocoded_dict[city]) == 1:
                    coordinates = geocode_df.loc[geocode_df["name_code"] == city]["Coordinates"].values[0].split(", ")
                    geocoded_dict[city].append(coordinates[0])
                    geocoded_dict[city].append(coordinates[1])
                    country_code = geocode_df.loc[geocode_df["name_code"] == city]["Country Code"].values[0]
                    geocoded_dict[city].append(country_code)
                    success_counter += 1
        # Otherwise check in alternate names
        elif geocode_df["Alternate Names"].str.contains(search_string, na = False).any():
            coordinates = geocode_df.loc[geocode_df["Alternate Names"].str.contains(search_string, na = False)].sort_values("Population")["Coordinates"].values[0].split(", ")
            geocoded_dict[city].append(coordinates[0])
            geocoded_dict[city].append(coordinates[1])
            country_code = geocode_df.loc[geocode_df["Alternate Names"].str.contains(search_string, na = False)].sort_values("Population")["Country Code"].values[0]
            geocoded_dict[city].append(country_code)
            success_counter += 1
        print("Done:", str((city_counter / len(geocoded_dict.keys()))*100)[:5], "% - Success:", str((success_counter / city_counter)*100)[:5], "%")
    geocoded_df = pd.DataFrame.from_dict(geocoded_dict, orient = "index")
    geocoded_df = geocoded_df.reset_index().reset_index().rename(columns = {"level_0": "id", "index": "name_code", 0: "name", 1: "lat", 2: "lon", 3: "country_code"})
    geocoded_df = geocoded_df.loc[geocoded_df["lat"].notna()]
    return geocoded_df
geocoded_df = geocoded_df_creator(geocoded_dict)
pd.DataFrame.to_csv(geocoded_df, path.join(dir, "geocoding", "geocoded.csv"), encoding = "utf-8", sep = ";", index = False)