import os
import numpy as np
import CorEx as ce
import time
from sklearn.naive_bayes import BernoulliNB
from sklearn import metrics
from imblearn.over_sampling import SMOTE
import multiprocessing
import pickle
import Sparse_Matrix_IO


__IF_TRAIN_WITHOUT_SAVE = True
__ROOT_MODEL = "/home/ubuntu/Weiyi/model_06_01_classprior"

__FEATURES = ["hour", "day", "country", "margin", "tmax", "bkc", "site_typeid", "site_cat", "browser_type",
             "bidder_id", "vertical_id", "bid_floor", "format", "product", "banner", "response"]
__FEATURES_TO_DROP = []

__DATA_FROM = 2
# Data Format = [[Prefix], [Suffix]]
# __TRAIN_DATA = [["all"], [i for i in range(5)]]
# __TEST_DATA = [["all"], [5]]

# Data Format = [[Month], [Day], [Hour]]
__TRAIN_DATA = [[6], [19]]
__TEST_DATA =  [[6], [20]]


def get_io_addr_random_sample(prefix, suffix):
    list_io_addr = []
    root = "/home/ubuntu/random_samples"
    for i in prefix:
        for j in suffix:
            file_name = i+"data"+str(j)
            addr_in = os.path.join(root, file_name+"_bin.npy")
            list_io_addr.append(addr_in)
    return list_io_addr


def get_io_addr(list_month, list_day):
    list_io_addr = []
    root = "/home/wlu/Desktop/rips16"
    for month in list_month:
        for day in list_day:
            io_addr = os.path.join(root,
                                   str(month).rjust(2, "0"),
                                   str(day).rjust(2, "0"))
            addr_in = os.path.join(io_addr, "day_samp_bin.npy")
            list_io_addr.append(addr_in)
    return list_io_addr


def discard_vars(X, cutoffs):
    print "Discarding selected features......"
    X_new = []
    for line in X:
        new_line = []
        for i in range(0, len(cutoffs), 2):
            new_line.extend(line[cutoffs[i]:cutoffs[i+1]])
        X_new.append(new_line)
    return np.array(X_new)


def correlation_ex(X):
    X = X[:, 31:224]
    layer = ce.Corex(n_hidden=5)
    layer.fit(X)
    return layer


def corex_transform(layer, X):
    Y = X[:, 31:224]
    Y = layer.transform(Y)
    X = np.hstack([X[:, 0:31], Y, X[:, 224:len(X[0])]])
    return X

def train(cutoffs):
    print "\n========== Start Training =========="
    if __DATA_FROM == 2:
        list_io_addr = get_io_addr(__TRAIN_DATA[0], __TRAIN_DATA[1])
    else:
        list_io_addr = get_io_addr_random_sample(__TRAIN_DATA[0], __TRAIN_DATA[1])
    clf = BernoulliNB(class_prior=[0.05, 0.95])

    if __IF_TRAIN_WITHOUT_SAVE:
        print "Performing correlation explanation......"
        with open("/home/wlu/Desktop/day_samp_bin_1-2.npy", "r") as file_in:
            X = Sparse_Matrix_IO.load_sparse_csr(file_in)
            if len(cutoffs) > 0:
                X = discard_vars(X, cutoffs)
            layer = correlation_ex(X)

    for i in range(0, len(list_io_addr)):
        path_in = list_io_addr[i]
        print "\nGenerating training set from {}".format(path_in)
        with open(path_in, "r") as file_in:
            X = Sparse_Matrix_IO.load_sparse_csr(file_in)

        if len(cutoffs) > 0:
            X = discard_vars(X, cutoffs)

        vector_len = len(X[0])
        X_train = X[:, 0:vector_len-1]
        y_train = X[:, vector_len-1]

        if __IF_TRAIN_WITHOUT_SAVE:
            print "Transforming training set according to CorEx......"
            X_train = corex_transform(layer, X_train)

        sm = SMOTE(ratio=0.95)
        X_train, y_train = sm.fit_sample(X_train, y_train)

        print "Fitting Model......"
        clf.partial_fit(X_train, y_train, classes=[0, 1])
        print "Done"

    if __IF_TRAIN_WITHOUT_SAVE:
        return [clf, layer]
    else:
        with open(__ROOT_MODEL, "w") as file_out:
            pickle.dump(clf, file_out)
        return []


def crawl(args):
    addr_in = args[0]
    clf = args[1]
    cutoffs = args[2]
    layer = None
    if __IF_TRAIN_WITHOUT_SAVE:
        layer = args[3]

    print "Processing testing set from {}".format(addr_in)
    with open(addr_in, "r") as file_in:
        X = Sparse_Matrix_IO.load_sparse_csr(file_in)

    if len(cutoffs) > 0:
        X = discard_vars(X, cutoffs)

    vector_len = len(X[0])
    X_test = X[:, 0:vector_len-1]
    y_test = X[:, vector_len-1]

    if __IF_TRAIN_WITHOUT_SAVE:
        X_test = corex_transform(layer, X_test)

    prediction = clf.predict(X_test)

    return metrics.confusion_matrix(y_test, prediction)


def test(cutoffs, args):
    print "\n========== Start Testing =========="
    print "\nLoad Model......"
    layer = None
    if __IF_TRAIN_WITHOUT_SAVE:
        clf = args[0]
        layer = args[1]
    else:
        with open(__ROOT_MODEL, "r") as file_in:
            clf = pickle.load(file_in)
    print "Done\n"

    if __DATA_FROM == 2:
        list_io_addr = get_io_addr(__TEST_DATA[0], __TEST_DATA[1])
    else:
        list_io_addr = get_io_addr_random_sample(__TEST_DATA[0], __TEST_DATA[1])

    confusion_matrix = [0, 0, 0, 0]
    args = []
    for i in range(len(list_io_addr)):
        args.append((list_io_addr[i], clf, cutoffs, layer))

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

start = time.time()
args = train(cutoffs)
print "----------Training Completed in {} seconds----------\n".format(round(time.time()-start, 2))

start = time.time()
test(cutoffs, args)
print "----------Testing Completed in {} seconds----------\n".format(round(time.time()-start, 2))
