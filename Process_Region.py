import json
import csv
import operator


result_list = []


def get_dates():
    may = [(5, i, j) for i in range(1, 8) for j in range(24)]
    # may = []
    june = [(6, i, j) for i in range(4, 26) for j in range(24)]
    # june = []
    return may+june


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
    dict_region = {}
    for result in result_list:
        for key in result:
            if dict_region.has_key(key):
                dict_region[key] += result[key]
            else:
                dict_region.update({key:result[key]})

    print "{} unique regions recorded".format(len(dict_region))
    sorted_domain = sorted(dict_region.items(), key=operator.itemgetter(1), reverse=True)
    with open("/home/ubuntu/Weiyi/regions.ods", "w") as file_out:
        wr = csv.writer(file_out)
        for item in sorted_domain:
            wr.writerow(item)
