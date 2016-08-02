import os
import numpy as np
from scipy import vstack
from imblearn.over_sampling import SMOTE
import Sparse_Matrix_IO as smio


# With a given address of the day to take random sample from,
# obtain a numpy matrix that contain 100,000 impressions,
# with the specified ratio of positive responses and negative responses,
# and return the feature matrix X and the corresponding response vector y
# The ratio is given by pos/neg
def get(addr_day, mode="normal", ratio=-1, sampling="None", bin=False):
    if not mode == "res":
        res = "Reservoir"
    else:
        res = ""

    if not ratio == -1:
        n = 100000
        neg = int(n / (1+ratio))
        pos = n - neg

        with open(os.path.join(addr_day, "PosNeg", res, "day_samp_new_neg.npy"), "r") as file_neg:
            matrix_neg = smio.load_sparse_csr(file_neg)
        matrix_neg = matrix_neg[:neg, :]
        with open(os.path.join(addr_day, "PosNeg", res, "day_samp_new_pos.npy"), "r") as file_pos:
            matrix_pos = smio.load_sparse_csr(file_pos)
        matrix_pos = matrix_pos[:pos, :]

        matrix = vstack((matrix_neg, matrix_pos))
        np.random.shuffle(matrix)
    else:
        with open(os.path.join(addr_day, res, "day_samp_new.npy"), "r") as file_in:
            matrix = smio.load_sparse_csr(file_in)

    width = np.size(matrix, 1)
    X = matrix[:, :width-1]
    y = matrix[:, width-1]

    if sampling == "Over":
        sm = SMOTE(ratio=0.95)
        X, y = sm.fit_sample(X, y)

    return X, y
