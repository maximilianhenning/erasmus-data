import pandas as pd
from os import path
from glob import glob

dir = path.dirname(__file__)
geocoded_df = pd.read_csv(path.join(dir, "geocoded.csv"), sep = ";", encoding = "utf-8")
target_years = []
edges_raw_folder = glob(path.join(dir, "edges_raw/*"))
for file in edges_raw_folder:
    year = file.split("edges_raw\\")[1].split(".")[0]
    target_years.append(year)
df_list = []
for year in target_years:
    df = pd.read_csv(path.join(dir, "edges_raw", str(year) + ".csv"), sep = ";", encoding = "utf-8")
    df = df.groupby(["home", "target"]).size().reset_index()
    # Rename to count
    df["time"] = year 
    df["home"] = df["home"].astype(int)
    df["target"] = df["target"].astype(int)
    df.rename(columns = {"home": "origin", "target": "dest", 0: "weight"}, inplace = True)
    print(len(df.index), df["weight"].sum())
    print(df.head())
    df.to_csv(path.join(dir + "/edges/" + str(year) + ".csv"), sep = ";", index = False)
# Combine all edges
#edges_list = []
#edges_raw_folder = glob(path.join(dir, "data/*"))
#for file in data_folder:
#    year = file.split("data\\")[1].split(".")[0]
#    data_years.append(year)