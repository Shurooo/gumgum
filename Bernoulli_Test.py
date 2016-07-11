import os
import numpy as np
import pickle
from sklearn import metrics
import Sparse_Matrix_IO


__ROOT_MODEL = "/home/ubuntu/Weiyi/model_05_01"
__ALPHA = [0.99+0.001*i for i in range(10)]


def get_io_addr():
    root = "/mnt/rips/2016"
    filename_in = "output_bin.npy"
    list_day = [i for i in range(1, 2)]
    list_hour = [22]
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


list_io_addr = get_io_addr()
with open(__ROOT_MODEL, "r") as file_in:
    clf = pickle.load(file_in)

for addr_in in list_io_addr:
    with open(addr_in, "r") as file_in:
        X = Sparse_Matrix_IO.load_sparse_csr(file_in)

    vector_len = len(X[0])
    X_test = X[:, 0:vector_len-1]
    y_test = X[:, vector_len-1]
    probas = clf.predict_proba(X_test)

    for alpha in __ALPHA:

        prediction = []
        for k in range(len(y_test)):
            if probas[k,0] > alpha:
                prediction.append(0)
            else:
                prediction.append(1)

        total = len(prediction)
        tn = 0
        tp = 0
        fp = 0
        fn = 0
        for i in range(total):
            if prediction[i]-y_test[i] == 0:
                if  prediction[i] == 1:
                    tp+=1
                else:
                    tn +=1
            else:
                if prediction[i] == 1:
                    fp +=1
                else:
                    fn +=1
        fitering = (tn + fn) / float(total)
        print 'filtering = ', fitering
        print 'recall = ', tp/ float(tp + fn)
        print metrics.precision_recall_fscore_support(y_test, prediction, average='binary', beta=12 )
        print metrics.confusion_matrix(y_test, prediction)


