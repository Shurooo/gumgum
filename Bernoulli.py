import os
import numpy as np
import time
from sklearn.naive_bayes import BernoulliNB
from sklearn import metrics
from imblearn.over_sampling import SMOTE
import multiprocessing
import pickle
import Sparse_Matrix_IO


__ROOT_MODEL = "/home/ubuntu/Weiyi/model_05_02"
__ALPHA = [0.99+0.001*i for i in range(10)]

# Data Format = [[Prefix], [Suffix]]
# __TRAIN_DATA = [["all"], [i for i in range(5)]]
# __TEST_DATA = [["all"], [5]]

# Data Format = [[Month], [Day], [Hour]]
__TRAIN_DATA = [[5], [1], [i for i in range(24)]]
__TEST_DATA =  [[5], [2], [i for i in range(24)]]


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
                addr_in = os.path.join(io_addr, "output_bin.npy")
                list_io_addr.append(addr_in)
    return list_io_addr


def train():
    print "\n========== Start Training =========="
    if len(__TRAIN_DATA) == 3:
        list_io_addr = get_io_addr(__TRAIN_DATA[0], __TRAIN_DATA[1], __TRAIN_DATA[2])
    else:
        list_io_addr = get_io_addr_random_sample(__TRAIN_DATA[0], __TRAIN_DATA[1])
    clf = BernoulliNB(fit_prior=True)

    for i in range(len(list_io_addr)):
        path_in = list_io_addr[i]
        print "\nGenerate training set from {}".format(path_in)
        with open(path_in, "r") as file_in:
            X = Sparse_Matrix_IO.load_sparse_csr(file_in)
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

    print "\nProcess testing set from {}".format(addr_in)
    with open(addr_in, "r") as file_in:
        X = Sparse_Matrix_IO.load_sparse_csr(file_in)
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


def test():
    print "\n========== Start Testing =========="
    print "\nLoad Model......"
    with open(__ROOT_MODEL, "r") as file_in:
        clf = pickle.load(file_in)
    print "Done"

    confusion_matrix_para = []
    for i in range(len(__ALPHA)):
        confusion_matrix_para.append([0, 0, 0, 0])

    if len(__TEST_DATA) == 3:
        list_io_addr = get_io_addr(__TEST_DATA[0], __TEST_DATA[1], __TEST_DATA[2])
    else:
        list_io_addr = get_io_addr_random_sample(__TEST_DATA[0], __TEST_DATA[1])

    args = []
    for i in range(len(list_io_addr)):
        args.append((list_io_addr[i], clf))

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

start = time.time()
train()
print "----------Training Completed in {} seconds----------\n".format(round(time.time()-start, 2))
start = time.time()
test()
print "----------Testing Completed in {} seconds----------\n".format(round(time.time()-start, 2))
