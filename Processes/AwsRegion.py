import json
import Get_Result_Output as gro


result_list = []


def run(addr_in):
    dict_awsr = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            if entry["em"].has_key("awsr"):
                awsr = entry["em"]["awsr"]
            else:
                awsr = "NONE"
            if dict_awsr.has_key(awsr):
                dict_awsr[awsr] += 1
            else:
                dict_awsr.update({awsr:1})

    return dict_awsr


def add_result(result):
    result_list.append(result)


def get_result():
    gro.get_result(result_list, "awsregions")
