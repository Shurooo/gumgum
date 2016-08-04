import os
import time
import operator
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn import metrics
from matplotlib import pylab as plt
import Sparse_Matrix_IO as smio


def get_data(month, day, hour=-1):
    if "wlu" in os.getcwd():
        root = "/home/wlu/Desktop/Data"
    else:
        root = "/mnt/rips2/2016"
    if hour == -1:
        addr_in = os.path.join(root,
                               str(month).rjust(2, "0"),
                               str(day).rjust(2, "0"),
                               "day_samp_new.npy")
    else:
        addr_in = os.path.join(root,
                               str(month).rjust(2, "0"),
                               str(day).rjust(2, "0"),
                               str(hour).rjust(2, "0"),
                               "output_new.npy")
    with open(addr_in, "r") as file_in:
        data = smio.load_sparse_csr(file_in)
    X = data[:, :-1]
    y = data[:, -1]
    return X, y


param = {'booster':'gbtree',   # Tree, not linear regression
         'objective':'binary:logistic',   # Output probabilities
         'eval_metric':['auc'],
         'bst:max_depth':5,   # Max depth of tree
         'bst:eta':.1,   # Learning rate (usually 0.01-0.2)
         'bst:gamma':0,   # Larger value --> more conservative
         'bst:min_child_weight':1,
         'scale_pos_weight':30,   # Often num_neg/num_pos
         'subsample':.8,
         'silent':1,   # 0 outputs messages, 1 does not
         'save_period':0,   # Only saves last model
         'nthread':6,   # Number of cores used; otherwise, auto-detect
         'seed':25}

data = (6, 4)

X_train, y_train = get_data(data[0], data[1])
X_test, y_test = get_data(data[0], data[1]+1)
data_train = xgb.DMatrix(X_train, label=y_train)

num_round = 250   # Number of rounds of training, increasing this increases the range of output values
bst = xgb.train(param, data_train, num_round, verbose_eval=0)


importance = sorted(bst.get_fscore().iteritems(), key=operator.itemgetter(1), reverse=True)
result_all = []
for k in range(100, 2501, 100):
    print "k = ", k
    selected = [int(item[0][1:]) for item in importance[:k]]

    X_train_Sel = X_train[:, selected]
    start = time.time()
    data_train = xgb.DMatrix(X_train_Sel, label=y_train)
    bst = xgb.train(param, data_train, num_round, verbose_eval=0)
    train_time = round(time.time() - start, 2)

    X_test_Sel = X_test[:, selected]
    data_test = xgb.DMatrix(X_test_Sel, label=y_test)

    prob = bst.predict(data_test)
    # J score, AUC score, best recall, best filter rate, best cutoff

    score = 0
    recall_best = 0
    filter_rate_best = 0
    net_savings_best = 0
    cut_best = 0
    for cutoff in range(10, 15):
        cut = cutoff/float(100)   # Cutoff in decimal form
        y_pred = prob > cut   # If y values are greater than the cutoff
        recall = metrics.recall_score(y_test, y_pred)
        filter_rate = sum(np.logical_not(y_pred))/float(len(prob))
        if recall*6.7+filter_rate > score:
            score = recall*6.7+filter_rate
            recall_best = recall
            filter_rate_best = filter_rate
            net_savings_best = -5200+127000*filter_rate-850000*(1-recall)
            cut_best = cut
    result_all.append([k, train_time, score, recall_best, filter_rate_best, cut_best, net_savings_best])
print result_all
np.save("/home/wlu/Desktop/Feature_Imp_Select", np.array(result_all))
