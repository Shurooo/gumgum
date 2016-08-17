"""
Define the method to parse variables "bidderid", "verticalid", "bidfloor", "format", "product", "w", and "h"
"""

import Shared as sd

formats_ = [16, 31, 9, 12, 14, 3, 2, 7, 5, 21, 8, 20, 15, 6, 22, 27, 25, 26, 30, 13, 23]

# ("w", "h") is set to (-1, -1) to indicate missing banners
banners_ = [(300, 250), (728, 90), (160, 600), (320, 50), (300, 600), (970, 90), (468, 60), (234, 60),
            (13, 13), (12, 12), (17, 17), (18, 18), (10, 10), (300, 120), (16, 16), (250, 100), (19, 19), (320, 480),
            (250, 70), (0, 0), (450, 100), (21, 21), (20, 20), (400, 400), (300, 100), (-1, -1)]


def process(margin, entry, result, mode):
    """
    Given a JSON object formatted by Extractor.py, parse variables "bidderid", "verticalid", "bidfloor", "format", "product", "w", and "h",
    and the results to the list of possible results.
    :param entry: the JSON object that represents one impression
    :param result: the list of possible results
    :return: None
    """

    # Auction - Bidrequests - bidder id
    bidder_id = entry["bidderid"]
    if bidder_id == 36:  # Adjusting the index for DSP 36 since we ignore DSP 35 and 37
        bidder_id = 35
    sd.binarize(result, bidder_id-1, 35)

    # Auction - Bidrequests - vertical id
    sd.binarize(result, entry["verticalid"]-1, 16)

    # Auction - Bidrequests - Impressions - bid Floor
    bid_floor = round(float(entry["bidfloor"]), 2)

    if bid_floor-margin == 0:
        result.append(0)
    else:
        result.append(1)

    # If bid floor is to be parsed into binary format, create a boolean variable for every interval of size 0.5 from 0 to 28,
    # and according to the value of the bid floor, set the associated boolean variable to 1.
    # Otherwise, just record the value of bid floor.
    if mode == "bin":
        index = 0
        if bid_floor < 28:
            index = int(bid_floor*20)
        bid_floor_list = [0]*560
        bid_floor_list[index] = 1
        result.extend(bid_floor_list)
    else:
        result.append(bid_floor)

    # Determine if bid floor is a multiple of 0.05 or of 0.1
    for n in [20, 10]:
        bid_floor_tmp = n*bid_floor
        if bid_floor_tmp == int(bid_floor_tmp):
            result.append(1)
        else:
            result.append(0)

    # Determine if bid floor is greater than the values in thres_list
    index = 0
    thres_list = [1.5, 2, 2.5, 3, 28]
    for thres in thres_list:
        if bid_floor > thres:
            result.append(1)
            index += 1
        else:
            n = len(thres_list) - index
            result.extend([0]*n)
            break

    # Auction - Bidrequests - Impressions - format
    sd.binarize(result, formats_.index(entry["format"]), len(formats_))

    # Auction - Bidrequests - Impressions - product
    sd.binarize(result, entry["product"]-1, 6)

    # Auction - Bidrequests - Impressions - banner
    width = entry["w"]
    height = entry["h"]

    # Determine if banner belongs to any of the following types:
    #   1) h in (0, 200] and w in (0, 500]
    #   2) h in (0, 200] and w in (500, infinity)
    #   3) h in (200, infinity) and w in (0, 500]
    banner_cat = [0, 0, 0]
    if 0 < height <= 200:
        if 0 < width <= 500:
            banner_cat[0] = 1
        elif width > 500:
            banner_cat[1] = 1
    elif (height > 200) and (width <= 500):
        banner_cat[2] = 1

    sd.add_to_result(result, (width, height), banners_)
    result.extend(banner_cat)


def get_hearder():
    """
    Return the names of features extracted in this section, and the number of variables used to represent each feature.
    :return: a list of tuples containing the feature names and the lengths of the corresponding features
    """
    bidder_id = ("bidder_id", 35)
    vertical_id = ("vertical_id", 16)
    bid_floor = ("bid_floor", 9)
    format = ("format", len(formats_))
    product = ("product", 6)
    banner = ("banner", 3+len(banners_)+1)

    return [bidder_id, vertical_id, bid_floor, format, product, banner]