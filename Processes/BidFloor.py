import json
import operator
import csv
import os


result_list = []


def run(addr_in):
    dict_bidfloor = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            auction = entry["auction"]
            bid_responded = []
            if auction.has_key("bids"):
                for bid in auction["bids"]:
                    bid_responded.append(bid["requestid"])

            for bidreq in auction["bidrequests"]:
                id = bidreq["id"]
                if_res = 0
                if id in bid_responded:
                    if_res = 1
                if bidreq.has_key("impressions"):
                    for imp in bidreq["impressions"]:
                        bidfloor = round(imp["bidfloor"], 2)
                        if dict_bidfloor.has_key(bidfloor):
                            dict_bidfloor[bidfloor][0] += 1
                            dict_bidfloor[bidfloor][1] += if_res
                        else:
                            dict_bidfloor.update({bidfloor:[1, if_res]})
    return dict_bidfloor


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

    print "{} unique {} recorded".format(len(dict_result), "bidfloors")
    sorted_result = sorted(dict_result.items(), key=operator.itemgetter(1), reverse=True)
    with open(os.path.join("/home/ubuntu/Weiyi", "bidfloors_new.ods"), "w") as file_out:
        wr = csv.writer(file_out)
        for item in sorted_result:
            var = item[0]
            req = item[1][0]
            res = item[1][1]
            ratio = round(float(res) / req, 4)
            wr.writerow((var, req, res, ratio))
