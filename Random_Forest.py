import os
import numpy as np
import time
from sklearn.naive_bayes import BernoulliNB
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import NearMiss
import Sparse_Matrix_IO


# Data Format = [[Month], [Day], [Hour]]
path_train = "/home/wlu/Desktop/random_samples/day_samp_0622_num.npy"
path_test = "/home/wlu/Desktop/random_samples/day_samp_0623_num.npy"


def train():
    print "\n>>>>> Start Training on {}".format(path_train)
    clf = RandomForestClassifier(n_estimators=70, max_features=4, max_depth=None, min_samples_split=1, n_jobs=-1, random_state=0, class_weight={0:0.001, 1:0.999})

    with open(path_train, "r") as file_in:
        X = Sparse_Matrix_IO.load_sparse_csr(file_in)

    vector_len = len(X[0])
    X_train = X[:, 0:vector_len-1]
    y_train = X[:, vector_len-1]

    sm = SMOTE(ratio=0.999)
    X_train, y_train = sm.fit_sample(X_train, y_train)

    print "Fitting Model......"
    clf.fit(X_train, y_train)
    print "Done"

    return clf


def thres(item, alpha):
    if item > alpha:
        return 0
    else:
        return 1


def test(clf):
    print "\n>>>>> Start Testing".format(path_test)

    confusion_matrix = [0, 0, 0, 0]

    with open(path_test, "r") as file_in:
        X = Sparse_Matrix_IO.load_sparse_csr(file_in)

    vector_len = len(X[0])
    X_test = X[:, 0:vector_len-1]
    y_test = X[:, vector_len-1]

    print "Making predictions"
    prediction_proba = clf.predict_proba(X_test)
    alpha = 0.9999
    prediction = [thres(item[0], alpha) for item in prediction_proba]
    result = metrics.confusion_matrix(y_test, prediction)

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
