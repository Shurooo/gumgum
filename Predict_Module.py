import os
import pickle
import numpy as np
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import Get_Data as gd
import Sparse_Matrix_IO as smio
import multiprocessing


__SAVE_MODEL = False
__ROOT_MODEL = "/home/ubuntu/Weiyi/model_random_forest.p"

__TRAIN_DATA = [(6, 4)]
__TEST_DATA =  [(6, 5)]

__FEATURES_TO_GET = ["bidder_id", "bid_floor", "country", "site_cat", "hour"]
# __FEATURES_TO_GET = []
__RATIO = 2.75

def get_io_addr(data_in):
    list_io_addr = []
    root = "/mnt/rips2/2016"
    for item in data_in:
        month = item[0]
        day = item[1]
        io_addr = os.path.join(root,
                               str(month).rjust(2, "0"),
                               str(day).rjust(2, "0"))
        addr_in = os.path.join(io_addr)
        list_io_addr.append(addr_in)
    return list_io_addr


def train(clf, data_train):
    list_io_addr = get_io_addr(data_train)

    if len(list_io_addr > 1):
        for path_in in list_io_addr:
            print "\n>>>>> Start Training on {}".format(path_in)
            clf.train_online(path_in)

    if __SAVE_MODEL:
        with open(__ROOT_MODEL, "w") as file_out:
            pickle.dump(clf, file_out)

    return clf


def crawl(args):
    addr_in = args[0]
    clf = args[1]

    X_test, y_test = gd.get(addr_day=addr_in, features_to_get=__FEATURES_TO_GET)
    prediction = clf.predict(X_test)

    return metrics.confusion_matrix(y_test, prediction)


def test(clf):
    print "\n========== Start Testing =========="
    print "\nLoad Model......"
    if __SAVE_MODEL:
        with open(__ROOT_MODEL, "r") as file_in:
            clf = pickle.load(file_in)
    print "Done\n"

    list_io_addr = get_io_addr(__TEST_DATA)

    confusion_matrix = [0, 0, 0, 0]
    args = []
    for i in range(len(list_io_addr)):
        args.append((list_io_addr[i], clf))

    p = multiprocessing.Pool(4)
    for result in p.imap(crawl, args):
        confusion_matrix[0] += result[1, 1]   # tp
        confusion_matrix[1] += result[0, 1]   # fp
        confusion_matrix[2] += result[0, 0]   # tn
        confusion_matrix[3] += result[1, 0]   # fn
    print "Done"

    print "\nGenerate statistics"
    tp = confusion_matrix[0]
    fp = confusion_matrix[1]
    tn = confusion_matrix[2]
    fn = confusion_matrix[3]
    total = tp+fp+tn+fn
    recall = tp / float(tp+fn)
    filtering = float(tn+fn) / total
    print "recall = {0:.4f}, filtering = {1:.4f}".format(round(recall, 4), round(filtering, 4))


def run_predict(clf, data):
    start = time.time()
    clf = train(clf, data[0])
    print "----------Training Completed in {} seconds----------\n".format(round(time.time()-start, 2))

    start = time.time()
    test(clf, data[1])
    print "----------Testing Completed in {} seconds----------\n".format(round(time.time()-start, 2))
