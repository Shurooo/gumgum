import multiprocessing
from datetime import datetime
from scipy.sparse import csr_matrix, vstack
import numpy as np
import os
import json


var_ = ["hour", "day", "cc", "rg", "margin", "tmax", "bkc", "typeid", "cat", "pcat", "domain", "bti", "bidderid", "verticalid", "bidfloor", "format", "product", "banner"]
with open("dict_all.json", "r") as file_in:
    dict_all = json.load(file_in)


def get_io_addr_day_samp():
    # may = [(5, i) for i in range(1, 8)]
    may = []
    june = [(6, i) for i in range(4, 5)]
    # june = []

    root = "/mnt/rips2/2016"
    filename_in = "day_samp_raw_test"
    filename_out = "day_samp_test_play.npy"

    list_io_addr = []
    for item in may+june:
        month = item[0]
        day = item[1]
        io_addr = os.path.join(root,
                               str(month).rjust(2, "0"),
                               str(day).rjust(2, "0"))
        addr_in = os.path.join(io_addr, filename_in)
        addr_out = os.path.join(io_addr, filename_out)
        list_io_addr.append((addr_in, addr_out))

    return list_io_addr


def get_value(entry, var):
    if var == "hour":
        t = entry["t"] / 1000
        value = datetime.fromtimestamp(t).hour
    elif var == "day":
        t = entry["t"] / 1000
        value = datetime.fromtimestamp(t).hour
    elif var == "banner":
        w = entry["w"]
        h = entry["h"]
        value = (w, h)
    elif var == "margin" or var == "bidfloor":
        value = round(entry[var], 2)
    else:
        value = entry[var]
    return value


def process(result, var, value, list_value, list_ratio):
    if var == "bkc":
        process_bkc(result, value, list_value, list_ratio)
    elif var == "domain":
        process_domain(result, value, list_value, list_ratio)
    elif var == "cat" or var == "pcat":
        process_cat(result, value, list_value, list_ratio)
    else:
        try:
            index = list_value.index(value)
            result.append(list_ratio[index])
        except:
            result.append(0)


def process_bkc(result, value, list_value, list_ratio):
    result_tmp = [0]*len(list_value)
    bkc_list = value.split(",")
    for item in bkc_list:
        if not item == "":
            bkc = int(item)
            try:
                index = list_value(bkc)
                result_tmp[index] = list_ratio[index]
            except:
                pass
    result.extend(result_tmp)


def process_domain(result, value, list_value, list_ratio):
    index = 0
    for item in list_value:
        if value in item:
            break
        index += 1
    if index < len(list_ratio):
        result.append(list_ratio[index])
    else:
        result.append(0)


def process_cat(result, value, list_value, list_ratio):
    result_tmp = [0]*len(list_value)
    for cat in value:
        if "IAB" in cat:
            cat_int = IAB_parser(cat)
            try:
                index = list_value.index(cat_int)
                result_tmp[index] = list_ratio[index]
            except:
                pass
    result.extend(result_tmp)


def IAB_parser(str):
    s = str.split("IAB")
    str = s[1]
    if not str.isdigit():
        s = str.split("-")  # Ignore sub-category like IAB1-3
        str = s[0]
    return int(str)


def crawl(io_addr):
    addr_in = io_addr[0]
    addr_out = io_addr[1]
    data_sparse_list = []
    with open(addr_in, "r") as file_in:
        print "Processing {}".format(addr_in)
        for line in file_in:
            result = []
            entry = json.loads(line)
            for var in var_:
                value = get_value(entry, var)
                dict_var = dict_all[var]
                list_value = dict_var[0]
                list_ratio = dict_var[1]
                process(result, var, value, list_value, list_ratio)

            result.append(entry["response"])
            print len(result)
            data_sparse_list.append(csr_matrix(result))

    data_matrix = vstack(data_sparse_list)
    with open(addr_out, 'w') as file_out:
            np.savez(file_out,
                     data=data_matrix.data,
                     indices=data_matrix.indices,
                     indptr=data_matrix.indptr,
                     shape=data_matrix.shape)

if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr_day_samp()

    for result in p.imap(crawl, list_io_addr):
        pass