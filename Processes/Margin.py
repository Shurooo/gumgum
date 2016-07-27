import json
import Get_Result_Output as gro


result_list = []


def run(addr_in):
    dict_margin = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            margin = round(entry["auction"]["margin"], 2)
            if dict_margin.has_key(margin):
                dict_margin[margin] += 1
            else:
                dict_margin.update({margin:1})
    return dict_margin


def add_result(result):
    result_list.append(result)


def get_result():
    gro.get_result(result_list, "margins")
