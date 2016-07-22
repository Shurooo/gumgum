import os
import pickle
import numpy as np
import time
from sklearn.naive_bayes import BernoulliNB
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import NearMiss
import Sparse_Matrix_IO
import multiprocessing


__SAVE_MODEL = True
__ROOT_MODEL = "/home/ubuntu/Weiyi/model_random_forest.p"

# Data Format = [[Prefix], [Suffix]]
# __TRAIN_DATA = [["all"], [i for i in range(5)]]
# __TEST_DATA = [["all"], [5]]

# Data Format = [[Month], [Day], [Hour]]
__TRAIN_DATA = [[6], [19]]
__TEST_DATA =  [[6], [20]]


def get_io_addr(data_in):
    list_io_addr = []
    if str(data_in[0][0]).isdigit():
        root = "/mnt/rips2/2016"
        list_month = data_in[0]
        list_day = data_in[1]
        for month in list_month:
            for day in list_day:
                io_addr = os.path.join(root,
                                       str(month).rjust(2, "0"),
                                       str(day).rjust(2, "0"))
                addr_in = os.path.join(io_addr, "day_samp_bin.npy")
                list_io_addr.append(addr_in)
    else:
        root = "/home/ubuntu/random_samples"
        list_prefix = data_in[0]
        list_suffix = data_in[1]
        for prefix in list_prefix:
            for suffix in list_suffix:
                file_name = prefix+"data"+str(suffix)
                addr_in = os.path.join(root, file_name+"_bin.npy")
                list_io_addr.append(addr_in)
    return list_io_addr


def train():
    clf = RandomForestClassifier(n_estimators=100, max_features=5, warm_start=True, max_depth=None, min_samples_split=1, n_jobs=-1, random_state=0, class_weight={0:1, 1:5000}, criterion="entropy")
    list_io_addr = get_io_addr(__TRAIN_DATA)

    for path_in in list_io_addr:
        with open(path_in, "r") as file_in:
            X = Sparse_Matrix_IO.load_sparse_csr(file_in)
        print "\n>>>>> Start Training on {}".format(path_in)

        vector_len = len(X[0])
        X_train = X[:, 0:vector_len-1]
        y_train = X[:, vector_len-1]

        # sm = SMOTE(ratio=0.95)
        # X_train, y_train = sm.fit_sample(X_train, y_train)

        print "Fitting Model......"
        clf.fit(X_train, y_train)
        print "Done"

    if __SAVE_MODEL:
        with open(__ROOT_MODEL, "w") as file_out:
            pickle.dump(clf, file_out)

    return clf


def thres(item, alpha):
    if item > alpha:
        return 0
    else:
        return 1


def crawl(args):
    addr_in = args[0]
    clf = args[1]

    print "Processing testing set from {}".format(addr_in)
    with open(addr_in, "r") as file_in:
        X = Sparse_Matrix_IO.load_sparse_csr(file_in)

    vector_len = len(X[0])
    X_test = X[:, 0:vector_len-1]
    y_test = X[:, vector_len-1]

    # prediction_proba = clf.predict_proba(X_test)
    # alpha = 0.9999
    # prediction = [thres(item[0], alpha) for item in prediction_proba]
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
