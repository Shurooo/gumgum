import json
import Get_Result_Output as gro


result_list = []


def run(addr_in):
    dict_country = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            if entry["em"].has_key("cc"):
                country = entry["em"]["cc"]
            else:
                country = "NONE"
            if dict_country.has_key(country):
                dict_country[country] += 1
            else:
                dict_country.update({country:1})

    return dict_country


def add_result(result):
    result_list.append(result)


def get_result():
    gro.get_result(result_list, "countries")
