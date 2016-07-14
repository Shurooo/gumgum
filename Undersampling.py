# Undersampling method
# Samples given proportion of negative responses, keeps all positive responses

import numpy as np
from scipy.sparse import csr_matrix
import random


def get(data):
    temp = np.load(data)
    d = csr_matrix((temp['data'], temp['indices'], temp['indptr']), shape=temp['shape'], dtype=float).toarray()
    return d


def split_helper(arr, cond):
    return [arr[cond], arr[~cond]]


def split(data):

    h = np.size(data, 0)
    w = np.size(data, 1)
    zero, one = split_helper(data, data[:, w-1] < 1)
    prop = np.size(one, 0)/h   # Proportion of positive responses
    return zero, one, prop


# Reservoir sample the 0s
def sample(data, numlines):
    sample = []
    n = 0
    for row in data:   # For each row in data:
        if n < numlines:
            sample.append(row)
            n += 1
        else:
            r = random.randint(0, n)
            if r < numlines:
                sample[r] = row
            n += 1
    return sample


def undersample(data, ratio):   # ratio is same as SMOTE ratio
    zero, one, prop = split(data)
    num_one = np.size(one, 0)
    numlines = int(num_one/ratio)
    zero = sample(zero, numlines)
    new = np.vstack([one, zero])
    return new
