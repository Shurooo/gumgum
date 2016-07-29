import os
import Event
import Auction
import Auction_Site
import Auction_BidRequests


def get_dict(var):
    dicts_root_ = "dicts"
    with open(os.path.join(dicts_root_, "dict_"+var+".txt"), "r") as file_in:
        dict_var = [line.rstrip("\r\n") for line in file_in]
    return dict_var


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
    binarize(result, index, len(dict_var))


def process(entry, result):
    Event.process(entry, result)
    margin = Auction.process(entry, result)
    Auction_Site.process(entry,result)
    Auction_BidRequests.process(margin, entry, result)
    # Response
    result.append(entry["response"])
