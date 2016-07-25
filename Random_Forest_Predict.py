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

# Data Format = [[Month], [Day], [Hour]]
__TRAIN_DATA = [[6], [4]]
__TEST_DATA =  [[6], [5]]

__FEATURES_TO_GET = ["bid_floor", "bidder_id", "format"]
__RATIO = 3 

def get_io_addr(data_in):
    list_io_addr = []
    root = "/mnt/rips2/2016"
    list_month = data_in[0]
    list_day = data_in[1]
    for month in list_month:
        for day in list_day:
            io_addr = os.path.join(root,
                                   str(month).rjust(2, "0"),
                                   str(day).rjust(2, "0"))
            addr_in = os.path.join(io_addr)
            list_io_addr.append(addr_in)
    return list_io_addr


def train():
    clf = RandomForestClassifier(n_estimators=40,
                                 max_features=4,
                                 min_weight_fraction_leaf=0.000001,
                                 oob_score=True,
                                 warm_start=False,
                                 n_jobs=-1,
                                 random_state=1514)
    list_io_addr = get_io_addr(__TRAIN_DATA)

    for path_in in list_io_addr:
        print "\n>>>>> Start Training on {}".format(path_in)
        X_train, y_train = gd.get(addr_day=path_in, ratio=__RATIO, features_to_get=__FEATURES_TO_GET)
        print "----------\n", len(X_train[0]), "\n----------"

        print "Fitting Model......"
        clf.fit(X_train, y_train)
        print "Done"

    if __SAVE_MODEL:
        with open(__ROOT_MODEL, "w") as file_out:
            pickle.dump(clf, file_out)

    return clf


def crawl(args):
    addr_in = args[0]
    clf = args[1]

    X_test, y_test = gd.get(addr_day=addr_in, features_to_get=__FEATURES_TO_GET)
    print "----------\n", len(X_test[0]), "\n----------"
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


start = time.time()
clf = train()
print "----------Training Completed in {} seconds----------\n".format(round(time.time()-start, 2))

start = time.time()
test(clf)
print "----------Testing Completed in {} seconds----------\n".format(round(time.time()-start, 2))
