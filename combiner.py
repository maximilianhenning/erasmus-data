import pandas as pd
from os import path
from glob import glob

def geocode_lookup(city, geocoded_df):
    number = geocoded_df.loc[geocoded_df["name_code"] == city].index
    return number

dir = path.dirname(__file__)
geocoded_df = pd.read_csv(path.join(dir, "geocoded.csv"), sep = ";", encoding = "utf-8")
target_years = range(2008, 2020)
df_list = []
for year in target_years:
    df = pd.read_csv(path.join(dir, "edges_raw", str(year) + ".csv"), sep = ";", encoding = "utf-8")
    df = df.groupby(["home", "target"]).size().reset_index()
    # Rename to count
    df["time"] = year 
    df["home"] = df["home"].astype(int)
    df["target"] = df["target"].astype(int)
    df.rename(columns = {"home": "origin", "target": "dest", 0: "weight"}, inplace = True)
    print(df.head())
    df.to_csv(path.join(dir + "/edges/" + str(year) + ".csv"), sep = ";", index = False)