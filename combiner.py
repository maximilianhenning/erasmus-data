import pandas as pd
from os import path, makedirs
from glob import glob

dir = path.dirname(__file__)
geocoded_df = pd.read_csv(path.join(dir, "geocoding/geocoded.csv"), sep = ";", encoding = "utf-8")
if not path.exists(path.join(dir + "/edges")):
    makedirs(path.join(dir + "/edges"))
if not path.exists(path.join(dir + "/output")):
    makedirs(path.join(dir + "/output"))

target_years = []
edges_raw_folder = glob(path.join(dir, "edges_raw/*"))
for file in edges_raw_folder:
    year = int(file.split("edges_raw\\")[1].split(".")[0])
    df = pd.read_csv(file, sep = ";", encoding = "utf-8")
    df = df.groupby(["home", "target"]).size().reset_index()
    df["time"] = year
    df["home"] = df["home"].astype(int)
    df["target"] = df["target"].astype(int)
    df.rename(columns = {"home": "origin", "target": "dest", 0: "count"}, inplace = True)
    df.to_csv(path.join(dir, "edges", str(year) + ".csv"), sep = ";", index = False)

# Combine all edges
edges_folder = glob(path.join(dir, "edges/*"))
df_list = []
for file in edges_folder:
    df = pd.read_csv(file, sep = ";", encoding = "utf-8")
    df_list.append(df)
unfiltered_df = pd.concat(df_list)
# Eliminate flows with only one person
final_df = unfiltered_df.loc[unfiltered_df["count"] > 1]
final_df.to_csv(path.join(dir, "output/flows.csv"), sep = ";", index = False)

# Filter geocoded only to cities in dataset
origin_list = final_df["origin"].tolist()
dest_list = final_df["dest"].tolist()
all_cities_list = list(set(origin_list + dest_list))
geocoded_df = pd.read_csv(path.join(dir, "geocoding/geocoded.csv"), sep = ";", encoding = "utf-8")
geocoded_df = geocoded_df.loc[geocoded_df["id"].isin(all_cities_list)].drop(columns = "name_code")
geocoded_df.to_csv(path.join(dir, "output/locations.csv"), sep = ";", index = False)

# Drop flows if cities are not geocoded