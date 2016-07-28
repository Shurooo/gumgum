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


def get_io_addr():
    may = [(5, i, j) for i in range(1, 8) for j in range(24)]
    june = [(6, i, j) for i in range(4, 26) for j in range(24)]

    filename_in = "part-00000"
    root_in = "/mnt/rips/2016"
    filename_out = "output_bin_2.npy"
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
                    auction_process(auction, result)
                    auction_site_process(auction, result)
                    auction_dev_process(auction, result)
                    auction_bidrequests_process(auction, result, result_list)

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

    hour = datetime.fromtimestamp(t).hour
    binarize(result, hour, 24)

    day = datetime.fromtimestamp(t).weekday()
    binarize(result, day, 7)

    try:
        add_to_result(result, entry["cc"], countries_)
    except:
        binarize(result, len(countries_), len(countries_)+1)
    try:
        add_to_result(result, entry["rg"], regions_)
    except:
        binarize(result, len(regions_)-1, len(regions_)+1)


def auction_process(auction, result):
    # Auction - Margin
    margin = round(float(auction["margin"]), 2)
    add_to_result(result, margin, margins_)

    # Auction - Tmax
    if auction.has_key("tmax"):
        tmax = auction["tmax"]
        if tmax < 85:
            tmax = 0
        elif tmax == 85:
            tmax = 1
        else:
            tmax = 2
    else:
        tmax = 3
    binarize(result, tmax, 4)

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


def auction_site_process(auction, result):
    # Auction - Site - Typeid
    site = auction["site"]
    binarize(result, site["typeid"]-1, 3)

    # Auction - Site - Cat
    # Auction - Site - Pcat
    for var in ["cat", "pcat"]:
        cat_process(result, site, var)


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


def auction_bidrequests_process(auction, result, result_list):
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
        auction_bidrequest_impressions_process(bidreq, bid_responded, result_bid, result_list)


def auction_bidrequest_impressions_process(bidreq, bid_responded, result_bid, result_list):
    bidreq_id = bidreq["id"]
    # Determine if this impression is responded by any DSP
    impid_responded = -1
    if bid_responded.has_key(bidreq_id):
        impid_responded = bid_responded[bidreq_id]

    for imp in bidreq["impressions"]:
        # Auction - Bidrequests - Impressions - Bid Floor
        result_imp = result_bid[:]
        bid_floor = int(imp["bidfloor"])    # Take the floor
        if bid_floor > 4:
            if bid_floor < 10:
                bid_floor = 4
            else:
                bid_floor = 5
        binarize(result_imp, bid_floor, 6)

        # Auction - Bidrequests - Impressions - Format
        format_index = __FORMAT_INDEX[imp["format"]]
        binarize(result_imp, format_index-1, len(__FORMAT_INDEX))

        # Auction - Bidrequests - Impressions - Product
        binarize(result_imp, imp["product"]-1, 6)

        # Auction - Bidrequests - Impressions - Banner
        if imp.has_key("banner"):
            width = imp["banner"]["w"]
            height = imp["banner"]["h"]
            if height <= 0 or width <= 0:
                banner = 1
            elif height < 400:
                if width < 500:
                    banner = 2
                else:
                    banner = 3
            else:
                if width < 500:
                    banner = 4
                else:
                    banner = 1
        else:
            banner = 0
        binarize(result_imp, banner, 5)

        # Response
        if imp["id"] == impid_responded:
            result_imp.append(1)
        else:
            result_imp.append(0)
        result_list.append(result_imp)


if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr()

    dumped = 0
    filtered = 0

    for result in p.imap(crawl, list_io_addr):
        dumped += result[0]
        filtered += result[1]

    print "{} lines filtered".format(filtered)
    print "{} lines dumped".format(dumped)

print "Completed in {} seconds\n".format(round(time.time()-start, 2))
