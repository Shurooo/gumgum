import json
import Get_Result_Output as gro


result_list = []


def run(addr_in):
    dict_tmax = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            if entry["auction"].has_key("tmax"):
                tmax = entry["auction"]["tmax"]
            else:
                tmax = "NONE"
            if dict_tmax.has_key(tmax):
                dict_tmax[tmax] += 1
            else:
                dict_tmax.update({tmax:1})

    return dict_tmax


def add_result(result):
    result_list.append(result)


def get_result():
    gro.get_result(result_list, "tmax")
