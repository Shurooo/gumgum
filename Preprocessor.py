import json
import numpy as np
from scipy.sparse import csr_matrix, vstack
from datetime import datetime
import os
import multiprocessing
import time


def get_dict(var):
    dicts_root_ = "dicts"
    with open(os.path.join(dicts_root_, "dict_"+var+".txt"), "r") as file_in:
        dict_var = [line.rstrip("\r\n") for line in file_in]
    return dict_var

countries_ = ["US", "GB", "CA", "DE", "FR", "NL", "IT"]
regions_ = get_dict("region")
margins_ = [3.5, 2.45, 3.0, 2.0, 1.65, 0.85, 1.25, 0.45, 0.25, 0.15, 0.1, 4.5, 0.0, 4.0]
bkcids_ = get_dict("bkc")
domains_ = get_dict("domain")
formats_ = [16, 31, 9, 12, 14, 3, 2, 7, 5, 21, 8, 20, 15, 6, 22, 27, 25, 26, 30, 13, 23]
browsers_ = [1, 2, 10, 13, 5, 11, 12, 7]
banners_ = [(300, 250), (728, 90), (160, 600), (320, 50), (300, 600), (970, 90), (468, 60), (234, 60), (13, 13),
            (12, 12), (17, 17), (18, 18), (10, 10), (300, 120), (16, 16), (250, 100), (19, 19), (320, 480),
            (250, 70), (0, 0), (450, 100), (21, 21), (20, 20), (400, 400), (300, 100)]

start = time.time()


def get_io_addr_day_samp():
    may = [(5, i) for i in range(2, 8)]
    june = [(6, i) for i in range(4, 26)]
    # june = []

    root = "/mnt/rips2/2016"
    filename_in = "day_samp_raw"
    filename_out = "day_samp_new.npy"

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


def get_io_addr_random_sample():
    list_io_addr = []
    root = "/home/ubuntu/random_samples"
    prefix = ["all"]
    suffix = [i for i in range(6)]
    for i in prefix:
        for j in suffix:
            file_name = i+"data"+str(j)
            addr_in = os.path.join(root, file_name+".txt")
            addr_out = os.path.join(root, file_name+"_new.npy")
            list_io_addr.append((addr_in, addr_out))
    return list_io_addr


def get_io_addr():
    may = [(5, i, j) for i in range(1, 2) for j in range(1)]
    june = [(6, i, j) for i in range(4, 26) for j in range(24)]
    # june = []

    filename_in = "part-00000"
    root_in = "/mnt/rips/2016"
    filename_out = "output2.npy"
    root_out = "/mnt/rips2/2016"

    list_dates = may + june
    list_io_addr = []
    for date in list_dates:
        month = date[0]
        day = date[1]
        hour = date[2]
        io_addr = os.path.join(str(month).rjust(2, "0"),
                               str(day).rjust(2, "0"),
                               str(hour).rjust(2, "0"))
        addr_in = os.path.join(root_in, io_addr, filename_in)
        path_out = os.path.join(root_out, io_addr)
        if not os.path.isdir(path_out):
            os.makedirs(path_out)
        addr_out = os.path.join(path_out, filename_out)
        list_io_addr.append((addr_in, addr_out))
    return list_io_addr


def crawl(io_addr):
    addr_in = io_addr[0]
    addr_out = io_addr[1]

    filtered = 0
    dumped = 0

    data_sparse_list = []
    if os.path.isfile(addr_in):
        with open(addr_in, "r") as file_in:
            print addr_in
            for line in file_in:
                try:
                    entry = json.loads(line)
                    result = []
                    result_list = []

                    auction = entry["auction"]
                    if_continue = filter(auction)   # Filter out auctions that do not contain any bid requests
                    if if_continue == 1:
                        filtered += 1
                        continue

                    event_process(entry, result)
                    margin = auction_process(auction, result)
                    auction_site_process(auction, result)
                    auction_dev_process(auction, result)
                    auction_bidrequests_process(margin, auction, result, result_list)

                    for item in result_list:
                        data_sparse_list.append(csr_matrix(item))

                except:
                    dumped += 1

        data_matrix = vstack(data_sparse_list)
        with open(addr_out, 'w') as file_out:
            np.savez(file_out,
                     data=data_matrix.data,
                     indices=data_matrix.indices,
                     indptr=data_matrix.indptr,
                     shape=data_matrix.shape)

    else:
        print "\nFile Missing: {}\n".format(addr_in)

    return [dumped, filtered]


def filter(auction):
    if not auction.has_key("bidrequests"):
        return 1
    else:
        bidreq_list = auction["bidrequests"]
        bidreq_list_copy =bidreq_list[:]
        index = 0
        for bidreq in bidreq_list_copy:
            if (bidreq["bidderid"] == 35 or bidreq["bidderid"] == 37) or (not bidreq.has_key("impressions")):
                bidreq_list.remove(bidreq)
                continue
            else:
                imp_list = bidreq["impressions"][:]
                for imp in imp_list:
                    # Filter out ad formats that should be ignored
                    if (not imp["format"] in formats_) or (imp["bidfloor"] < 0):
                        bidreq_list[index]["impressions"].remove(imp)
            if len(bidreq_list[index]["impressions"]) == 0:
                bidreq_list.remove(bidreq)
                continue
            index += 1
        if len(auction["bidrequests"]) == 0:
            return 1


def binarize(result, item, length):
    if item < 0:
        raise IndexError
    my_list = [0]*length
    my_list[item] = 1
    result.extend(my_list)


def add_to_result(result, var, dict_var):
    try:
        index = dict_var.index(var)
    except:
        index = len(dict_var)
    binarize(result, index, len(dict_var)+1)


def event_process(entry, result):
    event = entry["em"]
    t = event["t"] / 1000

    min = datetime.fromtimestamp(t).minute
    binarize(result, min, 60)

    hour = datetime.fromtimestamp(t).hour
    binarize(result, hour, 24)

    day = datetime.fromtimestamp(t).weekday()
    binarize(result, day, 7)

    hour_of_week = day*24+hour
    binarize(result, hour_of_week, 7*24)

    try:
        add_to_result(result, event["cc"], countries_)
    except:
        binarize(result, len(countries_), len(countries_)+1)
    try:
        add_to_result(result, event["rg"], regions_)
    except:
        binarize(result, len(regions_)-1, len(regions_)+1)


def if_multiple_tmax(result, tmax, n):
    tmax_tmp = tmax / float(n)
    if tmax_tmp == int(tmax_tmp):
        result.append(1)
    else:
        result.append(0)


def auction_process(auction, result):
    # Auction - Margin
    margin = round(float(auction["margin"]), 2)
    add_to_result(result, margin, margins_)

    # Auction - Tmax
    if auction.has_key("tmax"):
        tmax = auction["tmax"]

        # Determine if tmax is multiple of 5 or 10
        if_multiple_tmax(result, tmax, 5)
        if_multiple_tmax(result, tmax, 10)

        for thres in [500, 700]:
            if tmax <= thres:
                result.append(1)
            else:
                result.append(0)

        if tmax <= 20:
            result.append(1)
            result.extend([0]*80)
        elif tmax <= 85:
            result.append(0)
            result_tmp = [0]*65
            result_tmp[tmax-21] = 1
            result.extend(result_tmp)
            result.extend([0]*15)
        elif tmax <= 135:
            result.extend([0]*66)
            result_tmp = [0]*10
            result_tmp[(tmax-86) / 5] = 1
            result.extend(result_tmp)
            result.extend([0]*5)
        else:
            result.extend([0]*76)
            result_tmp = [0]*5
            if tmax <= 200:
                result_tmp[0] = 1
            elif tmax <= 500:
                result_tmp[1] = 1
            elif tmax <= 999:
                result_tmp[2] = 1
            elif tmax == 1000:
                result_tmp[3] = 1
            else:
                result_tmp[4] = 1
            result.extend(result_tmp)
    else:
        result.extend([0]*85)

    # Auction - BKC
    bkc_result = [0]*(len(bkcids_)+1)
    if auction["user"].has_key("bkc"):
        bkc_str = auction["user"]["bkc"]
        bkc_list = bkc_str.split(",")
        for item in bkc_list:
            try:
                index = bkcids_.index(item)
            except:
                index = len(bkcids_)
            bkc_result[index] = 1
    result.extend(bkc_result)

    return margin


def auction_site_process(auction, result):
    # Auction - Site - Typeid
    site = auction["site"]
    binarize(result, site["typeid"]-1, 3)

    # Auction - Site - Cat
    # Auction - Site - Pcat
    for var in ["cat", "pcat"]:
        cat_process(result, site, var)

    # Auction - Site - Domain
    index = 0
    try:
        domain = site["domain"]
        if (domain == "NONE") or (len(domain) == 0):
            index = len(domains_)
        else:
            for item in domains_:
                if item in domain:
                    break
                index += 1
    except:
        index = len(domains_)
    binarize(result, index, len(domains_)+1)


def cat_process(result, site, var):
    cats = [0]*26  # Parse 26 different types of IAB categories
    if site.has_key(var):
        for cat in site[var]:
            cat_int = IAB_parser(cat)
            cats[cat_int-1] = 1
    result.extend(cats)


def IAB_parser(str):
    s = str.split("IAB")
    str = s[1]
    if not str.isdigit():
        s = str.split("-")  # Ignore sub-category like IAB1-3
        str = s[0]
    return int(str)


def auction_dev_process(auction, result):
    try:
        add_to_result(result, auction["dev"]["bti"], browsers_)
    except:
        binarize(result, len(browsers_), len(browsers_)+1)


def auction_bidrequests_process(margin, auction, result, result_list):
    # Record the bid ids and corresonding impression ids that are responded if any
    bid_responded = {}
    if auction.has_key("bids"):
        for bid in auction["bids"]:
            bid_responded.update({bid["requestid"]:bid["impid"]})

    for bidreq in auction["bidrequests"]:
        result_bid = result[:]
        bidder_id = bidreq["bidderid"]
        # Adjusting the index for DSP 36 since we ignore DSP 35 and 37
        if bidder_id == 36:
            bidder_id = 35
        binarize(result_bid, bidder_id-1, 35)
        binarize(result_bid, bidreq["verticalid"]-1, 16)
        auction_bidrequest_impressions_process(margin, bidreq, bid_responded, result_bid, result_list)


def if_multiple_bid_floor(result_imp, bid_floor, n):
    bid_floor_tmp = n*bid_floor
    if bid_floor_tmp == int(bid_floor_tmp):
        result_imp.append(1)
    else:
        result_imp.append(0)


def auction_bidrequest_impressions_process(margin, bidreq, bid_responded, result_bid, result_list):
    bidreq_id = bidreq["id"]
    # Determine if this impression is responded by any DSP
    impid_responded = -1
    if bid_responded.has_key(bidreq_id):
        impid_responded = bid_responded[bidreq_id]

    for imp in bidreq["impressions"]:
        # Auction - Bidrequests - Impressions - Bid Floor
        result_imp = result_bid[:]
        bid_floor = round(float(imp["bidfloor"]), 2)
        if bid_floor-margin == 0:
            result_imp.append(0)
        else:
            result_imp.append(1)
        result_imp.append(bid_floor)

        # Determine if bid floor is a multiple of 0.05 or of 0.1
        if_multiple_bid_floor(result_imp, bid_floor, 20)
        if_multiple_bid_floor(result_imp, bid_floor, 10)

        index = 0
        thres_list = [1.5, 2, 2.5, 3, 28]
        for thres in thres_list:
            if bid_floor > thres:
                result_imp.append(1)
                index += 1
            else:
                n = len(thres_list) - index
                result_imp.extend([0]*n)
                break

        # Auction - Bidrequests - Impressions - Format
        binarize(result_imp, formats_.index(imp["format"]), len(formats_))

        # Auction - Bidrequests - Impressions - Product
        binarize(result_imp, imp["product"]-1, 6)

        # Auction - Bidrequests - Impressions - Banner
        banner_cat = [0, 0, 0]
        if imp.has_key("banner"):
            width = imp["banner"]["w"]
            height = imp["banner"]["h"]
            if 0 < height <= 200:
                if 0 < width <= 500:
                    banner_cat[0] = 1
                elif width > 500:
                    banner_cat[1] = 1
            elif (height > 200) and (width <= 500):
                banner_cat[2] = 1
            add_to_result(result_imp, (width, height), banners_)
        else:
            binarize(result_imp, len(banners_), len(banners_)+1)
        result_imp.extend(banner_cat)

        # Response
        if imp["id"] == impid_responded:
            result_imp.append(1)
        else:
            result_imp.append(0)
        result_list.append(result_imp)


if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr_day_samp()

    dumped = 0
    filtered = 0

    for result in p.imap(crawl, list_io_addr):
        dumped += result[0]
        filtered += result[1]

    print "{} lines filtered".format(filtered)
    print "{} lines dumped".format(dumped)

print "Completed in {} seconds\n".format(round(time.time()-start, 2))
