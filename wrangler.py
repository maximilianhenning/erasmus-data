import pandas as pd
import re
from os import path, makedirs
from glob import glob
from unidecode import unidecode

def read_df(year):
    year = int(year)
    if year == 2012:
        target_encoding = "latin-1"
    else:
        target_encoding = "utf-8"
    df = pd.read_csv(str(dir + "/data/" + str(year) + ".csv"), sep = ";", encoding = target_encoding)
    if year in [2008, 2009, 2010, 2011]:
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
    elif year in [2014, 2015, 2016, 2017, 2018, 2019]:
        home_column = "Sending City"
        target_column = "Receiving City"
        granularity = "city"
    return df, home_column, target_column, granularity

def city_lookup(institution_list, institution_city_dict, year, feature, len_overall):
    city_counter = 0
    city_list = []
    for institution in institution_list:
        city_counter += 1
        city_list.append(institution_city_dict[institution])
        print(year, feature, "city list created:", str(city_counter / len_overall * 100)[:5], "%")
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
        success_counter = 0
        fail_counter = 0
        len_overall = len(home_institution_list)
        for institution in institution_list:
            try:
                institution_city_dict[institution] = institutions_df.loc[institutions_df["Code"] == institution]["City"].values[0]
                success_counter += 1
            except:
                institution_city_dict[institution] = float("nan")
                fail_counter += 1
        print(year, "city lookup success:", str(success_counter / (success_counter + fail_counter) * 100)[:5], "%")
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
    for city_raw in city_list:
        city_counter += 1
        # Check if city_raw is nan
        if city_raw == city_raw:
            city = re.sub(r"\(.*?\)", "", city_raw)
            city = re.sub(r"\s\d+", "", city)
            city = city.lower().strip().replace("  ", " ")
            city = unidecode(city)
        try:
            number = geocoded_df.loc[geocoded_df["name_code"] == city]["id"].tolist()[0]
            success_counter += 1
        except:
            number = float("nan")
        city_coded_list.append(number)
        print(year, feature, "cities cleaned & id'd:", str(city_counter / len_overall * 100)[:5], 
            "% - Success:", str(success_counter / city_counter * 100)[:5], "%")
    return city_coded_list

# Load directory and initial dataframes
dir = path.dirname(__file__)
institutions_df = pd.read_csv(path.join(dir, "institutions.csv"), sep = ";", encoding = "utf-8")
geocoded_df = pd.read_csv(path.join(dir, "geocoded.csv"), sep = ";", encoding = "utf-8")

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
    if not path.exists(path.join(dir + "/edges_raw")):
        makedirs(path.join(dir + "/edges_raw"))
    df.to_csv(path.join(dir + "/edges_raw/" + str(year) + ".csv"), sep = ";", encoding = "utf-8")