import os
import time
import numpy as np
import XGB_Wrapper as xgbw
from sklearn import metrics
from sklearn.feature_selection import RFE
import Sparse_Matrix_IO as smio


# Feature Selection source:
## https://www.kaggle.com/sureshshanmugam/santander-customer-satisfaction/xgboost-with-feature-selection/code
# Another source to explore:
# https://www.kaggle.com/mmueller/liberty-mutual-group-property-inspection-prediction/xgb-feature-importance-python/code
# XGBoost 101 found at http://xgboost.readthedocs.io/en/latest/python/python_intro.html


if "wlu" in os.getcwd():
    root = "/home/wlu/Desktop/Data"
else:
    root = "/mnt/rips2/2016"


def get_data(month, day, hour=-1):
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


def search_cut(prob):
    score = 0
    recall_best = 0
    filter_rate_best = 0
    net_savings_best = 0
    cut_best = 0
    for cutoff in range(0, 31):
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
    return score, recall_best, filter_rate_best, cut_best, net_savings_best


data = (6, 4)

X_train, y_train = get_data(data[0], data[1])
X_test, y_test = get_data(data[0], data[1]+1)

# data_train = xgb.DMatrix(X_train, label=y_train)
# data_test = xgb.DMatrix(X_test, label=y_test)
#
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

num_round = 250   # Number of rounds of training, increasing this increases the range of output values
clf = xgbw.XGBWrapper(param, num_round, verbose_eval=0)

k = 500
step = 25
result_all = []

for step in [25, 50, 75]:
    selector = RFE(clf, step=step, n_features_to_select=k, verbose=2)

    print 'Fitting Selector'
    start = time.time()
    selector = selector.fit(X_train, y_train)
    train_time = time.time() - start

    support = selector.get_support(indices=True)
    file_name = str(data[0]).rjust(2, "0") + str(data[1]).rjust(2, "0") + "_k" + str(k) + "_s" + str(step),
    np.save(os.path.join("/home/ubuntu/Weiyi/RFE_Select", file_name), support)

    start = time.time()
    prob = selector.predict_proba(X_test)
    test_time = round(time.time() - start, 2)

    score, recall, filter_rate, cut, net_savings = search_cut(prob)
    result_all.append([k, train_time, test_time, score, recall, filter_rate, cut, net_savings, step])

np.save("/home/ubuntu/Weiyi/RFE_Select", np.array(result_all))