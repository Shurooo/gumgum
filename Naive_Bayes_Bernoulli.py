import os
import numpy as np
from sklearn.naive_bayes import BernoulliNB
from imblearn.over_sampling import SMOTE
import pickle
from scipy.sparse import csr_matrix


def save_sparse_csr(filename, array):
    array_sparse = csr_matrix(array)
    np.savez(filename, data=array.data, indices=array.indices, indptr=array.indptr, shape=array.shape)


def load_sparse_csr(filename):
    loader = np.load(filename)
    return csr_matrix((loader['data'], loader['indices'], loader['indptr']), shape=loader['shape']).toarray()


def get_io_addr():
    root = "/mnt/rips/2016"
    filename_in = "output_bin.npy"
    list_day = [i for i in range(1, 2)]
    list_hour = [i for i in range(20)]
    list_month = [5]

    list_io_addr = []
    for month in list_month:
        for day in list_day:
            if month == 6:
                day += 18
            for hour in list_hour:
                io_addr = os.path.join(root,
                                       str(month).rjust(2, "0"),
                                       str(day).rjust(2, "0"),
                                       str(hour).rjust(2, "0"))
                addr_in = os.path.join(io_addr, filename_in)
                list_io_addr.append(addr_in)
    return list_io_addr

clf = BernoulliNB()
list_io_addr = get_io_addr()

for i in range(len(list_io_addr)):
    path_in = list_io_addr[i]

    print "Processing {}".format(path_in)

    with open(path_in, "r") as file_in:
        X = load_sparse_csr(file_in)

    m = len(X[0])
    n = len(X)

    X_train = X[:, 0:m-1]
    y_train = X[:, m-1]

    print "Done"
    print

    sm = SMOTE(ratio=0.9)
    X_train_sm, y_train_sm = sm.fit_sample(X_train, y_train)

    print
    print "Fitting Model"
    clf.partial_fit(X_train_sm, y_train_sm, classes=[0, 1])
    print "Done"
    print

with open("/home/ubuntu/Weiyi/model_05_01", "w") as file_out:
    pickle.dump(clf, file_out)

