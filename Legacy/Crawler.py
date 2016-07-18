import os
import json
import multiprocessing
from functools import partial
import numpy as np
import matplotlib.pyplot as plt


ADDR_IN_ROOT = "/home/wlu/Desktop/rips16"
ADDR_OUT_ROOT = "/home/wlu/Desktop/rips16"

__HEADER = ["hour", "day", "country", "region", "margin", "tmax", "bkc", "site_typeid", "publisher_id", "browser_type",
             "bidder_id", "vertical_id", "bid_floor", "format", "product", "banner_width", "banner_height", "response"]
__HEADER[8:1] = ["site_cat {}".format(i+1) for i in range(26)]

__FEATURES = ["margin", "tmax", "bid_floor"]
__FEATURES_LEN = len(__FEATURES)
__INDICES = [__HEADER.index(__FEATURES[i]) for i in range(__FEATURES_LEN)]

list_a = [a for a in range(2,3)]
list_b = [b for b in range(1)]

def Crawl(B,A):
    p1 = str(A).rjust(2,'0')
    p2 = str(B).rjust(2,'0')

    list_features = []
    for i in range(__FEATURES_LEN):
        list_features.append([])
    path_in = os.path.join(ADDR_IN_ROOT, p1, p2, "output.ods")
    with open(path_in, "r") as data:
        print path_in
        next(data)
        for line in data:
            entries = line.split(',')
            for i in range(__FEATURES_LEN):
                item = entries[__INDICES[i]]
                list_features[i].append(float(item))

    return list_features

if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_features = []
    for i in range(__FEATURES_LEN):
        list_features.append([])
    for a in list_a:
        partial_Crawl = partial(Crawl, A = a)
        for result in p.imap(partial_Crawl, list_b):
            for i in range(__FEATURES_LEN):
                list_features[i].extend(result[i])

    for i in range(__FEATURES_LEN):
        hist, histograma3 = np.histogram(list_features, bins='sturges')
        print len(histograma3)
        histograma4 = plt.hist(list_features[i], bins='auto')
        print 'histograma4:->', histograma4
        plt.show()
