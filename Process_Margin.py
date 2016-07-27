import json
import csv
import operator


result_list = []


def get_dates():
    may = [(5, i, j) for i in range(1, 8) for j in range(24)]
    # may = []
    # june = [(6, i, j) for i in range(4, 26) for j in range(24)]
    june = []
    return may+june


def run(addr_in):
    dict_margin = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            margin = entry["auction"]["margin"]
            if dict_margin.has_key(margin):
                dict_margin[margin] += 1
            else:
                dict_margin.update({margin:1})
    return dict_margin


def add_result(result):
    result_list.append(result)


def get_result():
    dict_result = {}
    for result in result_list:
        for key in result:
            if dict_result.has_key(key):
                dict_result[key] += result[key]
            else:
                dict_result.update({key:result[key]})

    print "{} unique margins recorded".format(len(dict_result))
    sorted_result = sorted(dict_result.items(), key=operator.itemgetter(1), reverse=True)
    with open("/home/ubuntu/Weiyi/margins.ods", "w") as file_out:
        wr = csv.writer(file_out)
        for item in sorted_result:
            wr.writerow(item)
