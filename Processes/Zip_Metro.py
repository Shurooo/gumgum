import json
import operator
import csv
import os


result_list = []


def run(addr_in):
    dict_zips = {}
    dict_metros = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            if entry["em"].has_key("pc"):
                zip = entry["em"]["pc"]
            else:
                zip = "NONE"
            if dict_zips.has_key(zip):
                dict_zips[zip] += 1
            else:
                dict_zips.update({zip:1})

            if entry["em"].has_key("mc"):
                metro = entry["em"]["mc"]
            else:
                metro = "NONE"
            if dict_metros.has_key(metro):
                dict_metros[metro] += 1
            else:
                dict_metros.update({metro:1})

    return dict_zips, dict_metros


def add_result(result):
    result_list.append(result)


def get_result():
    for index in [0, 1]:
        dict_result = {}
        for result_tuple in result_list:
            result = result_tuple[index]
            for key in result:
                if dict_result.has_key(key):
                    dict_result[key] += result[key]
                else:
                    dict_result.update({key:result[key]})
        if index == 0:
            feature = "zips"
        else:
            feature = "metros"
        print "{} unique {} recorded".format(len(dict_result), feature)
        sorted_result = sorted(dict_result.items(), key=operator.itemgetter(1), reverse=True)
        with open(os.path.join("/home/ubuntu/Weiyi", feature + ".ods"), "w") as file_out:
            wr = csv.writer(file_out)
            for item in sorted_result:
                wr.writerow(item)
