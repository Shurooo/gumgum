from imblearn.over_sampling import SMOTE
import Undersampling as US
from sklearn.utils import column_or_1d
import numpy as np
import time
import os
from sklearn.metrics import make_scorer, fbeta_score
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn import metrics, grid_search
import Sparse_Matrix_IO as smio


__ADDR_OUT = "/home/ubuntu/Weiyi/GridSearch_Bern_66.txt"


def get_io_addr():
    list_month = [6]
    list_day = [i for i in range(4, 5)]
    list_io_addr = []
    root = "/mnt/rips2/2016"
    for month in list_month:
        for day in list_day:
            io_addr = os.path.join(root,
                                   str(month).rjust(2, "0"),
                                   str(day).rjust(2, "0"))
            addr_in = os.path.join(io_addr, "day_samp_bin.npy")
            list_io_addr.append(addr_in)
    return list_io_addr


def J_score(clf, X, y):
    y_pred = clf.predict(X)
    confusion_matrix = metrics.confusion_matrix(y, y_pred)
    tp = confusion_matrix[1, 1]
    fp = confusion_matrix[0, 1]
    tn = confusion_matrix[0, 0]
    fn = confusion_matrix[1, 0]
    total = len(y)
    recall = tp / float(tp+fn)
    filtered = float(tn) / total
    return recall + filtered / 5


def get_data(ratio, sampling):
    list_io_addr = get_io_addr()
    data = []
    for addr_in in list_io_addr:
        with open(addr_in, "r") as file_in:
            X = smio.load_sparse_csr(file_in)
            data.extend(X)
    data = np.array(data)

    n = 30000
    if sampling == "Over":
        m = int(np.size(data, 1))
        k = int(0.8*n)
        X = data[:n, :m-1]
        y = data[:n, m-1:]
        X_train = X[:k, :]
        y_train = y[:k]
        sm = SMOTE(ratio=ratio)
        X_train, y_train = sm.fit_sample(X_train, column_or_1d(y_train, warn=False))
        X_test = X[k:, :]
        y_test = y[k:]
    elif sampling == "None":
        m = int(np.size(data, 1))
        k = int(0.8*n)
        X = data[:n, :m-1]
        y = data[:n, m-1:].ravel()
        X_train = X[:k, :]
        y_train = y[:k]
        X_test = X[k:, :]
        y_test = y[k:]
    else:
        m = int(np.size(data, 1))
        k = int(0.2*np.size(data, 0))
        data_test = data[k:, :]
        data = data[:k, :]
        data = US.undersample(data, ratio)
        k = int(0.8*np.size(data, 0))
        if np.size(data_test, 0) > k:
            data_test = data[:k, :]
        X_train = data[:, :m-1]
        y_train = data[:, m-1:].ravel()
        X_test = data_test[:, :m-1]
        y_test = data_test[:, m-1:].ravel()
    return X_train, y_train, X_test, y_test


def lm():
    myfile = open(__ADDR_OUT, "w")

    for ratio in [-1]:
        sampling = "None"

        myfile.write("_____________________________________________\n")
        myfile.write(sampling+"Sampling Ratio = "+str(ratio))
        myfile.write("\n")

        X, y, X_test, y_test = get_data(ratio, sampling)
        classes_weights = []
        step = np.arange(0.5, 0.91, 0.1)
        for i in step:
            classes_weights.append([1-i, i])
        step = np.arange(0.91, 0.991, 0.01)
        for i in step:
            classes_weights.append([1-i, i])
        step = np.arange(0.991, 1, 0.001)
        for i in step:
            classes_weights.append([1-i, i])
        parameters = {"class_prior": classes_weights, "alpha": [0.5, 1, 1.5, 2]}

        gum_score = make_scorer(fbeta_score, beta = 10)  #using f1 score
        #gum_score = make_scorer(recall_score, beta = 12)  #using recall score
        clf = grid_search.GridSearchCV(BernoulliNB(), parameters, cv=3, scoring=J_score)

        start = time.time()
        print "fitting Multinomial NBs"
        clf.fit(X, y.ravel())
        elapsed1 = time.time()-start

        myfile.write("Best parameters set found on development set: ")
        myfile.write(str(clf.best_params_))
        myfile.write("\n")

        start = time.time()
        print "predicting"
        y_pred = clf.predict(X_test)
        elapsed2 = time.time()-start

        confusion_matrix = metrics.confusion_matrix(y_test, y_pred)
        tp = confusion_matrix[1, 1]
        fp = confusion_matrix[0, 1]
        tn = confusion_matrix[0, 0]
        fn = confusion_matrix[1, 0]
        total = tp+fp+tn+fn
        try:
            recall = round(tp / float(tp+fn), 4)
        except:
            recall = -1
        try:
            filtered = round(float(tn) / total, 4)
        except:
            filtered = -1

        myfile.write("Recall: \n")
        myfile.write(str(recall))
        myfile.write("\n")

        myfile.write("Filtered: \n")
        myfile.write(str(filtered))
        myfile.write("\n")

        myfile.write("Time to fit: " + str(elapsed1) + "\n")
        myfile.write("Time to predict: " + str(elapsed2) + "\n")

    myfile.close()

lm()
