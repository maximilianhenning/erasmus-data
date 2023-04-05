from os import path
from glob import glob
import re
import pandas as pd
from unidecode import unidecode

dir = path.dirname(__file__)
institutions_df = pd.read_csv(path.join(dir, "institutions.csv"), sep = ";", encoding = "utf-8")
geocoded_df = pd.read_csv(path.join(dir, "geocoded.csv"), sep = ";", encoding = "utf-8")

columns_dict = {}
target_years = range(2008, 2020)
for year in target_years:
    year = str(year)
    if year == "2012":
        target_encoding = "latin-1"
    else:
        target_encoding = "utf-8"
    df = pd.read_csv(str(dir + "/data/" + str(year) + ".csv"), sep = ";", encoding = target_encoding)
    if year in ["2008", "2009", "2010", "2011"]:
        home_institution_column = "HOMEINSTITUTION"
        target_institution_column = "HOSTINSTITUTION"
    elif year == "2012":
        home_institution_column = "HOME_INSTITUTION_CDE"
        target_institution_column = "HOST_INSTITUTION_CDE"
    elif year == "2013":
        home_institution_column = "SendingPartnerErasmusID"
        target_institution_column = "HostingPartnerErasmusID"
    elif year in ["2014", "2015", "2016", "2017", "2018"]:
        home_city_column = "Sending City"
        target_city_column = "Receiving City"
    elif year == "2019":
        home_city_column = "Sending City"
        target_city_column = "Receiving City"
    if home_institution_column:
        home_institution_list = df[home_institution_column].tolist()
        target_institution_list = df[target_institution_column].tolist()
        home_city_list = []
        target_city_list = []
        home_counter = 0
        target_counter = 0
        institution_city_dict = {}
        institution_list = home_institution_list + target_institution_list
        institution_list = list(set(institution_list))
        complete_length = len(home_institution_list)
        for institution in institution_list:
            try:
                institution_city_dict[institution] = institutions_df.loc[institutions_df["Code"] == institution]["City"].values[0]
            except:
                institution_city_dict[institution] = "nan"
        for institution in home_institution_list:
            home_counter += 1
            print(year, "home cities found:", str(home_counter / complete_length*100), "%")
            try:
                home_city_list.append(institution_city_dict[institution])
            except:
                home_city_list.append("nan")
        for institution in target_institution_list:
            target_counter += 1
            print(year, "target cities found:", str(target_counter / complete_length*100), "%")
            try:
                target_city_list.append(institution_city_dict[institution])
            except:
                target_city_list.append("nan")
    else:
        home_city_list = df[home_city_column].tolist()
        target_city_list = df[target_city_column].tolist()
    # Progress here
    complete_length = len(home_city_list)
    home_city_cleaned_list = []
    home_code_list = []
    target_city_cleaned_list = []
    target_code_list = []
    city_counter = 0
    target_counter = 0
    for city_raw in home_city_list:
        city_counter += 1
        print(year, "home cities cleaned & indexed:", city_counter / complete_length*100, "%")
        city = re.sub(r"\(.*?\)", "", city_raw)
        city = re.sub(r"\s\d+", "", city)
        city = city.lower().strip().replace("  ", " ")
        city = unidecode(city)
        home_city_cleaned_list.append(city)
        try:
            number = geocoded_df.index[geocoded_df["name_code"] == city].tolist()[0]
        except:
            number = "nan"
        home_code_list.append(number)
    for city_raw in target_city_list:
        target_counter += 1
        print(year, "target cities cleaned & indexed:", target_counter / complete_length*100, "%")
        city = re.sub(r"\(.*?\)", "", city_raw)
        city = re.sub(r"\s\d+", "", city)
        city = city.lower().strip().replace("  ", " ")
        city = unidecode(city)
        target_city_cleaned_list.append(city)
        try:
            number = geocoded_df.index[geocoded_df["name_code"] == city].tolist()[0]
        except:
            number = "nan"
        target_code_list.append(number)
    lists = [home_city_list, home_city_cleaned_list, home_code_list, target_city_list, target_city_cleaned_list, target_code_list]
    df = pd.DataFrame(lists).transpose()
    df.columns = ["home_raw", "home_name", "home", "target_raw", "target_name", "target"]
    print(df.head())
    df.to_csv(path.join(dir + "/edges_raw/" + str(year) + ".csv"), sep = ";", encoding = "utf-8")
    for var in ["home_institution_column", "home_city_column", "target_institution_column", "target_city_column"]:
        if var in locals():
            del var