import os
import numpy as np
import time
from sklearn.naive_bayes import BernoulliNB
from sklearn import metrics
from imblearn.over_sampling import SMOTE
import multiprocessing
import pickle
import Sparse_Matrix_IO


__ROOT_MODEL = "/home/ubuntu/Weiyi/model_06_01"
__ALPHA = [0.99+0.001*i for i in range(10)]

__FEATURES = ["hour", "day", "country", "margin", "tmax", "bkc", "site_typeid", "site_cat", "browser_type",
             "bidder_id", "vertical_id", "bid_floor", "format", "product", "banner", "response"]
__FEATURES_TO_DROP = []

# Data Format = [[Prefix], [Suffix]]
# __TRAIN_DATA = [["all"], [i for i in range(5)]]
# __TEST_DATA = [["all"], [5]]

# Data Format = [[Month], [Day], [Hour]]
__TRAIN_DATA = [[6], [1], [i for i in range(24)]]
__TEST_DATA =  [[6], [2], [i for i in range(24)]]


def get_io_addr_random_sample(prefix, suffix):
    list_io_addr = []
    root = "/home/ubuntu/random_samples"
    for i in prefix:
        for j in suffix:
            file_name = i+"data"+str(j)
            addr_in = os.path.join(root, file_name+"_bin.npy")
            list_io_addr.append(addr_in)
    return list_io_addr


def get_io_addr(list_month, list_day, list_hour):
    list_io_addr = []
    root = "/mnt/rips/2016"
    for month in list_month:
        for day in list_day:
            if month == 6:
                day += 18
            for hour in list_hour:
                io_addr = os.path.join(root,
                                       str(month).rjust(2, "0"),
                                       str(day).rjust(2, "0"),
                                       str(hour).rjust(2, "0"))
                addr_in = os.path.join(io_addr, "output_bin_new.npy")
                list_io_addr.append(addr_in)
    return list_io_addr


def discard_vars(X, cutoffs):
    X_new = []
    for line in X:
        new_line = []
        for i in range(0, len(cutoffs), 2):
            new_line.extend(line[cutoffs[i]:cutoffs[i+1]])
        X_new.append(new_line)
    return np.array(X_new)


def train(cutoffs):
    print "\n========== Start Training =========="
    if len(__TRAIN_DATA) == 3:
        list_io_addr = get_io_addr(__TRAIN_DATA[0], __TRAIN_DATA[1], __TRAIN_DATA[2])
    else:
        list_io_addr = get_io_addr_random_sample(__TRAIN_DATA[0], __TRAIN_DATA[1])
    clf = BernoulliNB(fit_prior=True)

    for i in range(len(list_io_addr)):
        path_in = list_io_addr[i]
        print "\nGenerating training set from {}".format(path_in)
        with open(path_in, "r") as file_in:
            X = Sparse_Matrix_IO.load_sparse_csr(file_in)

        if len(cutoffs) > 0:
            print "Discarding selected features......"
            X = discard_vars(X, cutoffs)

        vector_len = len(X[0])
        X_train = X[:, 0:vector_len-1]
        y_train = X[:, vector_len-1]
        print "Done"

        sm = SMOTE(ratio=0.9)
        X_train_sm, y_train_sm = sm.fit_sample(X_train, y_train)

        print "Fitting Model......"
        clf.partial_fit(X_train_sm, y_train_sm, classes=[0, 1])
        print "Done"

    with open(__ROOT_MODEL, "w") as file_out:
        pickle.dump(clf, file_out)


def crawl(args):
    addr_in = args[0]
    clf = args[1]
    cutoffs = args[2]

    print "Processing testing set from {}".format(addr_in)
    with open(addr_in, "r") as file_in:
        X = Sparse_Matrix_IO.load_sparse_csr(file_in)

    if len(cutoffs) > 0:
        X = discard_vars(X, cutoffs)

    vector_len = len(X[0])
    X_test = X[:, 0:vector_len-1]
    y_test = X[:, vector_len-1]
    probas = clf.predict_proba(X_test)

    list_confusion_matrix = []
    for i in range(len(__ALPHA)):
        prediction = []
        for k in range(len(y_test)):
            if probas[k,0] > __ALPHA[i]:
                prediction.append(0)
            else:
                prediction.append(1)
        list_confusion_matrix.append(metrics.confusion_matrix(y_test, prediction))
    return list_confusion_matrix


def test(cutoffs):
    print "\n========== Start Testing =========="
    print "\nLoad Model......"
    with open(__ROOT_MODEL, "r") as file_in:
        clf = pickle.load(file_in)
    print "Done\n"

    confusion_matrix_para = []
    for i in range(len(__ALPHA)):
        confusion_matrix_para.append([0, 0, 0, 0])

    if len(__TEST_DATA) == 3:
        list_io_addr = get_io_addr(__TEST_DATA[0], __TEST_DATA[1], __TEST_DATA[2])
    else:
        list_io_addr = get_io_addr_random_sample(__TEST_DATA[0], __TEST_DATA[1])

    args = []
    for i in range(len(list_io_addr)):
        args.append((list_io_addr[i], clf, cutoffs))

    p = multiprocessing.Pool(4)
    for result in p.imap(crawl, args):
        for i in range(len(result)):
            confusion_matrix_para[i][0] += result[i][1, 1]   # tp
            confusion_matrix_para[i][1] += result[i][0, 1]   # fp
            confusion_matrix_para[i][2] += result[i][0, 0]   # tn
            confusion_matrix_para[i][3] += result[i][1, 0]   # fn
    print "Done"

    print "\nGenerate statistics"
    for i in range(len(__ALPHA)):
        tp = confusion_matrix_para[i][0]
        fp = confusion_matrix_para[i][1]
        tn = confusion_matrix_para[i][2]
        fn = confusion_matrix_para[i][3]
        total = tp+fp+tn+fn
        recall = tp / float(tp+fn)
        filtering = float(tn+fn) / total
        print "alpha = {0:.3f}, recall = {1:.4f}, filtering = {2:.4f}".format(__ALPHA[i], round(recall, 4), round(filtering, 4))


def get_feature_indices():
    get_feature_length = {
        "hour": 24,
        "day": 7,
        "country": 193,
        "margin": 5,
        "tmax": 4,
        "bkc": 1,
        "site_typeid": 3,
        "site_cat": 26,
        "browser_type": 9,
        "bidder_id": 35,
        "vertical_id": 16,
        "bid_floor": 6,
        "format": 20,
        "product": 6,
        "banner": 5,
        "response": 1
    }
    feature_indices = {}
    begin = 0
    end = 0
    for item in __FEATURES:
        length = get_feature_length[item]
        end += length
        feature_indices.update({item:(begin, end)})
        begin += length
    return feature_indices, end


def get_cutoffs():
    feature_indices, total_length = get_feature_indices()
    cutoffs = [0, total_length]
    for item in __FEATURES_TO_DROP:
        indices = feature_indices[item]
        cutoffs.append(indices[0])
        cutoffs.append(indices[1])

    return sorted(cutoffs)


if len(__FEATURES_TO_DROP) > 0:
    cutoffs = get_cutoffs()
else:
    cutoffs = []

# start = time.time()
# train(cutoffs)
# print "----------Training Completed in {} seconds----------\n".format(round(time.time()-start, 2))
start = time.time()
test(cutoffs)
print "----------Testing Completed in {} seconds----------\n".format(round(time.time()-start, 2))
