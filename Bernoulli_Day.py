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


def get_addr_in(result):
    # Date Format = [(Month, Day)]
    may = [(5, i) for i in range(1, 8)]
    # june = [(6, i) for i in range(4, 26)]
    june = []
    total = [may, june]
    train_test_pairs = []
    root = "/mnt/rips2/2016"
    for dates in total:
        for i in range(len(dates)-1):
            train = dates[i]
            test = dates[i+1]
            file_train = os.path.join(str(train[0]).rjust(2, "0"), str(train[1]).rjust(2, "0"))
            file_test = os.path.join(str(test[0]).rjust(2, "0"), str(test[1]).rjust(2, "0"))
            addr_train = os.path.join(root, file_train)
            addr_test = os.path.join(root, file_test)

            train_test_pairs.append((addr_train, addr_test))
            result.append(file_train+"~"+file_test)
    return train_test_pairs


def train(addr_train, sampling):
    if sampling == "None":
        clf = BernoulliNB(class_prior=[0.05, 0.95])
        param = "cp=[0.05 0.95]"
    else:
        clf = BernoulliNB(class_prior=[0.01, 0.99])
        param = "cp=[0.01 0.99]"

    path_in = os.path.join(addr_train, "day_samp_bin.npy")
    with open(path_in, "r") as file_in:
        X = smio.load_sparse_csr(file_in)

    vector_len = len(X[0])
    X_train = X[:, 0:vector_len-1]
    y_train = X[:, vector_len-1]

    if sampling == "Over":
        ratio = 0.95
        sm = SMOTE(ratio=ratio)
        param += "; ratio={}".format(ratio)
        X_train, y_train = sm.fit_sample(X_train, y_train)
    elif sampling == "Under":
        ratio = 0.5
        X = US.undersample(X, ratio)
        param += "; ratio={}".format(ratio)
        vector_len = len(X[0])
        X_train = X[:, 0:vector_len-1]
        y_train = X[:, vector_len-1]

    clf.fit(X_train, y_train)

    if __SAVE_MODEL:
        model_name = "BNB_" + sampling + "_Model"
        path_out = os.path.join(addr_train, model_name)
        with open(path_out, "w") as file_out:
            pickle.dump(clf, file_out)

    return clf, param


def test(addr_test, clf):
    path_in = os.path.join(addr_test, "day_samp_model")
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


with open("/home/ubuntu/Weiyi/report.csv", "w") as file_out:
    wr = csv.writer(file_out, quoting = csv.QUOTE_MINIMAL)
    wr.writerow(["Model", "Training", "Sampling", "TN", "FP", "FN", "TP", "Recall", "Filtered", "Parameters"])

    result = ["BNB"]
    train_test_pairs = get_addr_in(result)
    for pair in train_test_pairs:
        for sampling in ["None"]:
            result.append(sampling)

            addr_train = pair[0]
            print "\n>>>>> Start Training on {}".format(addr_train)
            start = time.time()
            clf, param = train(addr_train, sampling)
            print ">>>>> Training on {0} completed in {1} seconds\n".format(addr_train, round(time.time()-start, 2))

            addr_test = pair[1]
            print "\n>>>>> Start Testing on {}".format(addr_test)
            start = time.time()
            stats = test(addr_test, clf)
            print ">>>>> Testing on {0} completed in {1} seconds\n".format(addr_test, round(time.time()-start, 2))

            result.extend(stats)
            result.append(param)
            wr.writerow(result)
