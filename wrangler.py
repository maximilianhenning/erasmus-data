import pandas as pd
import re
from os import path, makedirs
from glob import glob
from unidecode import unidecode

def read_df(year):
    year = int(year)
    if year in [2012, 2020]:
        target_encoding = "latin-1"
    else:
        target_encoding = "utf-8"
    df = pd.read_csv(path.join(dir, "data", str(year) + ".csv"), sep = ";", encoding = target_encoding)
    if year < 2012:
        home_column = "HOMEINSTITUTION"
        target_column = "HOSTINSTITUTION"
        granularity = "institution"
    elif year == 2012:
        home_column = "HOME_INSTITUTION_CDE"
        target_column = "HOST_INSTITUTION_CDE"
        granularity = "institution"
    elif year == 2013:
        home_column = "SendingPartnerErasmusID"
        target_column = "HostingPartnerErasmusID"
        granularity = "institution"
    elif year > 2013:
        home_column = "Sending City"
        target_column = "Receiving City"
        granularity = "city"
    df = df.loc[df[home_column].notna()]
    df = df.loc[df[target_column].notna()]
    if not path.exists(path.join(dir, "data_notna")):
        makedirs(path.join(dir, "data_notna"))
    df.to_csv(path.join(dir, "data_notna", str(year) + ".csv"), sep = ";", encoding = "utf-8")
    return df, home_column, target_column, granularity

def city_lookup(institution_list, institution_city_dict, year, feature, len_overall):
    institution_counter = 0
    city_list = []
    for institution in institution_list:
        institution_counter += 1
        if institution in institution_city_dict.keys():
            city_list.append(institution_city_dict[institution])
        else:
            city_list.append(str(institution).split(" ")[-1])
        print(year, feature, "city list created:", str(institution_counter / len_overall * 100)[:5], "%")
    return city_list

def create_city_lists(df, home_column, target_column, granularity):
    if granularity == "institution":
        home_institution_list = df[home_column].tolist()
        target_institution_list = df[target_column].tolist()
        # Create institution - city dictionary for all institutions
        institution_city_dict = {}
        institution_list = home_institution_list + target_institution_list
        institution_list = list(set(institution_list))
        # Monitoring
        len_overall = len(home_institution_list)
        for institution in institution_list:
            try:
                try:
                    institution_city_dict[institution] = institutions_df.loc[institutions_df["Code"] == institution]["City"].values[0]
                except:
                    institution = re.sub(r"\s*\d+", "", institution)
                    institution_city_dict[institution] = institutions_df.loc[institutions_df["Code"].str.contains(institution)]["City"].values[0]
            except:
                pass
        # Look up all cities in dictionary created above
        home_city_list = city_lookup(home_institution_list, institution_city_dict, year, "home", len_overall)
        target_city_list = city_lookup(target_institution_list, institution_city_dict, year, "target", len_overall)
    else:
        home_city_list = df[home_column].tolist()
        target_city_list = df[target_column].tolist()
    return home_city_list, target_city_list

# Clean city names, look up id in geocoded df
def code_city_lists(city_list, feature, geocoded_df):
    # Monitoring
    len_overall = len(city_list)
    city_counter = 0
    success_counter = 0
    city_coded_list = []
    city_coded_dict = {}
    for city in city_list:
        city_counter += 1
        # City string cleaning
        city = str(city)
        city = re.sub(r"\(.*?\)", "", city)
        city = re.sub(r"\s*\d+", "", city)
        city = city.lower().strip().replace("  ", " ")
        city = unidecode(city)
        # Use a new dict to speed up the process
        if city not in city_coded_dict.keys():
            try:
                city_coded_dict[city] = geocoded_df.loc[geocoded_df["name_code"] == city]["id"].tolist()[0]
            except:
                city_coded_dict[city] = "nan"
        if city_coded_dict[city] != "nan":
            success_counter += 1
        city_coded_list.append(city_coded_dict[city])
        print(year, feature, "cities cleaned & id'd:", str(city_counter / len_overall * 100)[:5], 
            "% - Success:", str(success_counter / city_counter * 100)[:5], "%")
    return city_coded_list

# Load directory and initial dataframes
dir = path.dirname(__file__)
institutions_df = pd.read_csv(path.join(dir, "geocoding/institutions.csv"), sep = ";", encoding = "utf-8")
geocoded_df = pd.read_csv(path.join(dir, "geocoding/geocoded.csv"), sep = ";", encoding = "utf-8")

# Glob files in data and done folders to see what years still need to be done
data_years = []
data_folder = glob(path.join(dir, "data/*"))
for file in data_folder:
    year = file.split("data\\")[1].split(".")[0]
    data_years.append(year)
done_years = []
done_folder = glob(path.join(dir, "edges_raw/*"))
for file in done_folder:
    year = file.split("edges_raw\\")[1].split(".")[0]
    done_years.append(year)
target_years = sorted(list(set(data_years) - set(done_years)))

# Iterate through target years
for year in target_years:
    df, home_column, target_column, granularity = read_df(year)
    home_city_list, target_city_list = create_city_lists(df, home_column, target_column, granularity)
    home_coded_list = code_city_lists(home_city_list, "home", geocoded_df)
    target_coded_list = code_city_lists(target_city_list, "target", geocoded_df)
    lists = [home_coded_list, target_coded_list]
    df = pd.DataFrame(lists).transpose()
    df.columns = ["home", "target"]
    if not path.exists(path.join(dir, "edges_raw")):
        makedirs(path.join(dir, "edges_raw"))
    df.to_csv(path.join(dir, "edges_raw", str(year) + ".csv"), sep = ";", encoding = "utf-8")