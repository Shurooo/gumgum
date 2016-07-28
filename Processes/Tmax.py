import json
import operator
import csv
import os


result_list = []


def run(addr_in):
    dict_tmax = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            auction = entry["auction"]
            if auction.has_key("tmax"):
                tmax = auction["tmax"]
            else:
                tmax = "NONE"
            count_req = 0
            if auction.has_key("bidrequests"):
                count_req = len(auction["bidrequests"])
            count_res = 0
            if auction.has_key("bids"):
                count_res = len(auction["bids"])
            if dict_tmax.has_key(tmax):
                dict_tmax[tmax][0] += count_req
                dict_tmax[tmax][1] += count_res
            else:
                dict_tmax.update({tmax:[count_req, count_res]})
    return dict_tmax


def add_result(result):
    result_list.append(result)


def get_result():
    dict_result = {}
    for result in result_list:
        for key in result:
            if dict_result.has_key(key):
                dict_result[key][0] += result[key][0]
                dict_result[key][1] += result[key][1]
            else:
                dict_result.update({key:result[key]})

    print "{} unique {} recorded".format(len(dict_result), "tmax")
    sorted_result = sorted(dict_result.items(), key=operator.itemgetter(1), reverse=True)
    with open(os.path.join("/home/ubuntu/Weiyi", "tmax_new.ods"), "w") as file_out:
        wr = csv.writer(file_out)
        for item in sorted_result:
            wr.writerow((item[0], item[1][0], item[1][1]))
