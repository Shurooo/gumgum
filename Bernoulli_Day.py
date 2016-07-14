import os
import numpy as np
import time
from sklearn.naive_bayes import BernoulliNB
from sklearn import metrics
from imblearn.over_sampling import SMOTE
import Undersampling as US
import multiprocessing
import pickle
import csv
import Sparse_Matrix_IO as smio


__SAVE_MODEL = True


def format_addr(dates, mode):
    root = "/mnt/rips2/2016"
    train_test_pairs = []
    dates_pairs = []
    for i in range(len(dates)-mode):
        train = dates[i]
        test = dates[i+mode]
        file_train = os.path.join(str(train[0]).rjust(2, "0"), str(train[1]).rjust(2, "0"))
        file_test = os.path.join(str(test[0]).rjust(2, "0"), str(test[1]).rjust(2, "0"))
        addr_train = os.path.join(root, file_train)
        addr_test = os.path.join(root, file_test)

        train_test_pairs.append((addr_train, addr_test))
        dates_pairs.append(file_train+"~"+file_test)
    return train_test_pairs, dates_pairs

def get_addr_in(mode):
    # Date Format = [(Month, Day)]
    may = [(5, i) for i in range(1, 8)]
    # june = [(6, i) for i in range(4, 26)]
    june = []

    pairs_by_month = []

    if mode == "Next_day":
        for dates in [may, june]:
            tuple_pairs = format_addr(dates, 1)
            pairs_by_month.append(tuple_pairs)
    else:
        tuple_pairs = format_addr(june, 7)
        pairs_by_month.append(tuple_pairs)

    return pairs_by_month


def train(addr_train, clf, sampling, onoff_line):

    path_in = os.path.join(addr_train, "day_samp_bin.npy")
    with open(path_in, "r") as file_in:
        X = smio.load_sparse_csr(file_in)

    vector_len = len(X[0])
    X_train = X[:, 0:vector_len-1]
    y_train = X[:, vector_len-1]

    if sampling == "Over":
        ratio = 0.95
        sm = SMOTE(ratio=ratio)
        X_train, y_train = sm.fit_sample(X_train, y_train)
    elif sampling == "Under":
        ratio = 0.5
        X = US.undersample(X, ratio)
        vector_len = len(X[0])
        X_train = X[:, 0:vector_len-1]
        y_train = X[:, vector_len-1]

    if onoff_line == "Offline":
        clf.fit(X_train, y_train)
    else:
        clf.partial_fit(X_train, y_train, classes=[0,1])

    if __SAVE_MODEL:
        model_name = "BNB_" + onoff_line +"_" + sampling + "_Model"
        path_out = os.path.join(addr_train, model_name)
        with open(path_out, "w") as file_out:
            pickle.dump(clf, file_out)

    return clf


def test(addr_test, clf):
    path_in = os.path.join(addr_test, "day_samp_bin.npy")
    with open(path_in, "r") as file_in:
        X = smio.load_sparse_csr(file_in)
    vector_len = len(X[0])
    X_test = X[:, 0:vector_len-1]
    y_test = X[:, vector_len-1]

    prediction = clf.predict(X_test)

    confusion_matrix = metrics.confusion_matrix(y_test, prediction)

    tp = confusion_matrix[1, 1]
    fp = confusion_matrix[0, 1]
    tn = confusion_matrix[0, 0]
    fn = confusion_matrix[1, 0]
    total = tp+fp+tn+fn
    recall = tp / float(tp+fn)
    filtered = float(tn+fn) / total
    return [tn, fp, fn, tp, recall, filtered]


def init_clf(sampling):
    clf_options = {
        "None": (BernoulliNB(class_prior=[0.05, 0.95]), "cp=[0.05 0.95]"),
        "Over": (BernoulliNB(class_prior=[0.01, 0.99]), "cp=[0.01 0.99]; ratio=0.95"),
        "Under": (BernoulliNB(class_prior=[0.01, 0.99]), "cp=[0.01 0.99]; ratio=0.5")
    }
    return clf_options[sampling]


with open("/home/ubuntu/Weiyi/report.csv", "w") as file_out:
    wr = csv.writer(file_out, quoting = csv.QUOTE_MINIMAL)
    wr.writerow(["Model", "Online/Offline", "Sampling", "Train~Test", "TN", "FP", "FN", "TP", "Recall", "Filtered", "Parameters"])

    for mode in ["Next_day"]:
        pairs_by_month = get_addr_in(mode)

        for item in pairs_by_month:
            train_test_pairs = item[0]
            dates_pairs = item[1]

            result = ["BNB"]
            for onoff_line in ["Online", "Offline"]:
                result_onoff = result[:]
                result_onoff.append(onoff_line)

                for sampling in ["Under"]:
                    result_sampling = result_onoff[:]
                    result_sampling.append(sampling)
                    clf, param = init_clf(sampling)

                    for i in range(len(train_test_pairs)):
                        pair = train_test_pairs[i]
                        result_final = result_sampling[:]
                        result_final.append(dates_pairs[i])
                        if onoff_line == "Offline":
                            clf, param = init_clf(sampling)

                        addr_train = pair[0]
                        print "\n>>>>> Start Training on {}".format(addr_train)
                        start = time.time()
                        clf = train(addr_train, clf, sampling, onoff_line)
                        print ">>>>> Training on {0} completed in {1} seconds".format(addr_train, round(time.time()-start, 2))

                        addr_test = pair[1]
                        print "\n>>>>> Start Testing on {}".format(addr_test)
                        start = time.time()
                        stats = test(addr_test, clf)
                        print ">>>>> Testing on {0} completed in {1} seconds".format(addr_test, round(time.time()-start, 2))

                        result_final.extend(stats)
                        result_final.append(param)
                        wr.writerow(result_final)
