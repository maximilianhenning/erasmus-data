import pandas as pd
import re
from os import path, makedirs
from glob import glob
from unidecode import unidecode

dir = path.dirname(__file__)
institutions_df = pd.read_csv(path.join(dir, "institutions.csv"), sep = ";", encoding = "utf-8")
geocoded_df = pd.read_csv(path.join(dir, "geocoded.csv"), sep = ";", encoding = "utf-8")

columns_dict = {}
target_years = range(2008, 2020)
done_years = [2008, 2009, 2010, 2011, 2012]
target_years -= done_years
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
        institution_city_dict = {}
        institution_list = home_institution_list + target_institution_list
        institution_list = list(set(institution_list))
        # Look up cities for all institutions
        # Monitoring
        success_counter = 0
        fail_counter = 0
        len_overall = len(home_institution_list)
        for institution in institution_list:
            try:
                institution_city_dict[institution] = institutions_df.loc[institutions_df["Code"] == institution]["City"].values[0]
                success_counter += 1
            except:
                institution_city_dict[institution] = "nan"
                fail_counter += 1
        print(year, "city lookup success:", str(success_counter / (success_counter + fail_counter) * 100),
            "% - Fail:", str(fail_counter / (success_counter + fail_counter)[:5] * 100),
            )
        # Create lists of home and target cities
        # Monitoring
        city_counter = 0
        for institution in home_institution_list:
            city_counter += 1
            home_city_list.append(institution_city_dict[institution])
            print(year, "home city list created:", str(city_counter / len_overall * 100)[:5], "%")
        city_counter = 0
        for institution in target_institution_list:
            city_counter += 1
            target_city_list.append(institution_city_dict[institution])
            print(year, "target city list created:", str(city_counter / len_overall * 100)[:5], "%")
    else:
        home_city_list = df[home_city_column].tolist()
        target_city_list = df[target_city_column].tolist()
    # Clean up city names, look up index in geocoded df
    complete_length = len(home_city_list)
    home_city_cleaned_list = []
    home_code_list = []
    target_city_cleaned_list = []
    target_code_list = []
    # Monitoring
    city_counter = 0
    success_counter = 0
    fail_counter = 0
    for city_raw in home_city_list:
        city_counter += 1
        city = re.sub(r"\(.*?\)", "", city_raw)
        city = re.sub(r"\s\d+", "", city)
        city = city.lower().strip().replace("  ", " ")
        city = unidecode(city)
        home_city_cleaned_list.append(city)
        try:
            number = geocoded_df.index[geocoded_df["name_code"] == city].tolist()[0]
            success_counter += 1
        except:
            number = "nan"
            fail_counter += 1
        home_code_list.append(number)
        print(year, "cities cleaned & indexed:", city_counter / len_overall * 100, 
            "% - Success:", str(success_counter / (success_counter + fail_counter) * 100)[:5])
    # Monitoring
    city_counter = 0
    success_counter = 0
    fail_counter = 0
    for city_raw in target_city_list:
        city_counter += 1
        city = re.sub(r"\(.*?\)", "", city_raw)
        city = re.sub(r"\s\d+", "", city)
        city = city.lower().strip().replace("  ", " ")
        city = unidecode(city)
        target_city_cleaned_list.append(city)
        try:
            number = geocoded_df.index[geocoded_df["name_code"] == city].tolist()[0]
            success_counter += 1
        except:
            number = "nan"
            fail_counter += 1
        target_code_list.append(number)
        print(year, "cities cleaned & indexed:", city_counter / len_overall * 100, 
            "% - Success:", str(success_counter / (success_counter + fail_counter) * 100)[:5])
    # Final processing
    lists = [home_code_list, target_code_list]
    df = pd.DataFrame(lists).transpose()
    df.columns = ["home", "target"]
    if not path.exists(path.join(dir + "/edges_raw")):
        makedirs(path.join(dir + "/edges_raw"))
    df.to_csv(path.join(dir + "/edges_raw/" + str(year) + ".csv"), sep = ";", encoding = "utf-8")
    # Clean up variables
    for var in ["home_institution_column", "home_city_column", "target_institution_column", "target_city_column"]:
        if var in locals():
            del var