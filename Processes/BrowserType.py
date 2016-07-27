import json
import Get_Result_Output as gro


result_list = []


def run(addr_in):
    dict_broswer = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            try:
                broswer = entry["auction"]["dev"]["bti"]
                if dict_broswer.has_key(broswer):
                    dict_broswer[broswer] += 1
                else:
                    dict_broswer.update({broswer: 1})
            except:
                pass
    return dict_broswer


def add_result(result):
    result_list.append(result)


def get_result():
    gro.get_result(result_list, "browsers")
