import multiprocessing
from datetime import datetime
import operator
import json
import csv
import os


# var_ = ["cc", "rg", "margin", "tmax", "typeid", "bti", "bidderid", "verticalid", "bidfloor", "format", "product", "cat", "pcat", "domain", "bkc", "t", "w", "h"]
var_ = ["margin", "h"]


def get_io_addr():
    may = [(5, i, j) for i in range(1, 2) for j in range(1)]
    # may = []
    # june = [(6, i, j) for i in range(4, 26) for j in range(24)]
    june = []

    root = "/mnt/rips2/2016"
    list_io_addr = []
    for item in may+june:
        month = item[0]
        day = item[1]
        hour = item[2]
        io_addr = os.path.join(root,
                               str(month).rjust(2, "0"),
                               str(day).rjust(2, "0"),
                               str(hour).rjust(2, "0"))
        addr_in = os.path.join(io_addr)
        list_io_addr.append(addr_in)
    return list_io_addr


def add_to_dict(dict_var, value, res):
    if dict_var.has_key(value):
        dict_var[value][0] += 1
        dict_var[value][1] += res
    else:
        dict_var.update({value:[1, res]})


def process_var(index, dict_list, entry, res, var):
    value = entry[var]
    if var == "bidfloor" or var == "margin":
        value = round(value, 2)
    add_to_dict(dict_list[index], value, res)


def IAB_parser(str):
    s = str.split("IAB")
    str = s[1]
    if not str.isdigit():
        s = str.split("-")  # Ignore sub-category like IAB1-3
        str = s[0]
    return int(str)


def process_cat(index, dict_list, entry, res, var):
    dict_var = dict_list[index]
    for cat in entry[var]:
        if "IAB" in cat:
            cat_int = IAB_parser(cat)
            add_to_dict(dict_var, cat_int, res)


def process_domain(index, dict_list, entry, res):
    domain_tmp = entry["domain"].split("www.")
    domain = domain_tmp[len(domain_tmp)-1]
    add_to_dict(dict_list[index], domain, res)


def process_bkc(index, dict_list, entry, res):
    dict_var = dict_list[index]
    bkc_list = entry["bkc"].split(",")
    for bkc in bkc_list:
        add_to_dict(dict_var, bkc, res)


def process_time(index, dict_list, entry, res):
    t = entry["t"] / 1000
    hour = datetime.fromtimestamp(t).hour
    add_to_dict(dict_list[index], hour, res)
    day = datetime.fromtimestamp(t).weekday()
    add_to_dict(dict_list[index+1], day, res)


def process_banner(index, dict_list, entry, res):
    w = entry["w"]
    h = entry["h"]
    add_to_dict(dict_list[index+1], (w, h), res)


def foo():
    print "foo"


def switch(var, dict_list, index, entry, res):
    print ">>>>> switch", var
    options = {
        "bidfloor": None,
        "margin": foo(),
        "cat": process_cat(index, dict_list, entry, res, var),
        "pcat": process_cat(index, dict_list, entry, res, var),
        "domain": process_domain(index, dict_list, entry, res),
        "bkc": process_bkc(index, dict_list, entry, res),
        "t": process_time(index, dict_list, entry, res),
        "w":process_banner(index, dict_list, entry, res)
    }
    try:
        dumb = options[var]
        print "Yes"
    except:
        dumb = process_var(index, dict_list, entry, res, var)
        print "No"


def crawl(path_in):
    print "Processing {}".format(path_in)
    dict_list = []
    for i in range(len(var_)):
        dict_list.append({})

    for suffix in ["pos", "neg"]:
        if suffix == "pos":
            res = 1
        else:
            res = 0
        addr_in = os.path.join(path_in, "output_test_"+suffix)
        with open(addr_in) as file_in:
            for line in file_in:
                entry = json.loads(line)
                for i in range(len(var_)-1):
                    switch(var_[i], dict_list, i, entry, res)

    return dict_list


if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr()

    dict_list = []
    for i in range(len(var_)):
        dict_list.append({})

    for result in p.imap(crawl, list_io_addr):
        for i in range(len(dict_list)):
            dict_var = dict_list[i]
            result_var = result[i]
            for key in result_var:
                if dict_var.has_key(key):
                    dict_var[key][0] += result_var[key][0]
                    dict_var[key][1] += result_var[key][1]
                else:
                    dict_var.update({key:[result_var[key][0], result_var[key][1]]})

    # for i in range(len(var_)):
    #     var = var_[i]
    #     if var == "t":
    #         var = "hour"
    #     elif var == "w":
    #         var = "day"
    #     elif var == "h":
    #         var = "banner"
    #     print "{} unique {} recorded".format(len(dict_list[i]), var)

        # sorted_result = sorted(dict_list[i].items(), key=operator.itemgetter(1), reverse=True)
        # with open(os.path.join("/home/ubuntu/Weiyi/Play", var+".ods"), "w") as file_out:
        #     wr = csv.writer(file_out)
        #     for item in sorted_result:
        #         req = item[1][0]
        #         res = item[1][1]
        #         ratio = round(float(res) / req, 4)
        #         wr.writerow((var, ratio))
