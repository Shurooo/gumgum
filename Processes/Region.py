import json
import Get_Result_Output as gro


result_list = []


def run(addr_in):
    dict_region = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            if entry["em"].has_key("rg"):
                region = entry["em"]["rg"]
            else:
                region = "NONE"
            if dict_region.has_key(region):
                dict_region[region] += 1
            else:
                dict_region.update({region:1})

    return dict_region


def add_result(result):
    result_list.append(result)


def get_result():
    gro.get_result(result_list, "regions")
