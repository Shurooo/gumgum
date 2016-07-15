from imblearn.over_sampling import SMOTE
from sklearn.utils import column_or_1d
import Undersampling as US
import Sparse_Matrix_IO as smio
from sklearn.naive_bayes import BernoulliNB
from sklearn import metrics
import numpy as np


__ADDR_IN = "/home/wlu/Desktop/rips16/05/01/day_samp_bin.npy"


def get_data(ratio, sampling):
    with open(__ADDR_IN, "r") as file_in:
        data = smio.load_sparse_csr(file_in)
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
    else:
        m = int(np.size(data, 1))
        k = int(0.8*np.size(data, 0))
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


X_train, y_train, X_test, y_test = get_data(0.9, "Under")
clf = BernoulliNB()
clf.fit(X_train, y_train.ravel())

y_pred = clf.predict(X_test)

confusion_matrix = metrics.confusion_matrix(y_test, y_pred)

print confusion_matrix

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
