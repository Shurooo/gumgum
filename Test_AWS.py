from imblearn.over_sampling import SMOTE
from sklearn.utils import column_or_1d
import Undersampling as US
import Sparse_Matrix_IO as smio
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
        data = US.undersample(data, ratio)
        m = int(np.size(data, 1))
        k = int(0.8*np.size(data, 0))
        X = data[:, :m-1]
        y = data[:, m-1:]
        X_train = X[:k, :]
        y_train = y[:k]
        X_test = X[k:, :]
        y_test = y[k:]
    return X_train, y_train, X_test, y_test
