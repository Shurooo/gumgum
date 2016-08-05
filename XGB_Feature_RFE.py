import os
import json
import numpy as np
from sklearn import metrics
from sklearn.feature_selection import RFE
import XGB_Wrapper as xgbw
import Sparse_Matrix_IO as smio


# Feature Selection source:
## https://www.kaggle.com/sureshshanmugam/santander-customer-satisfaction/xgboost-with-feature-selection/code
# Another source to explore:
# https://www.kaggle.com/mmueller/liberty-mutual-group-property-inspection-prediction/xgb-feature-importance-python/code
# XGBoost 101 found at http://xgboost.readthedocs.io/en/latest/python/python_intro.html


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

selector = RFE(clf, step=100, n_features_to_select=500, verbose=2)
print 'Selector fit...'
selector = selector.fit(X_train, y_train)
support = selector.get_support(indices=True)
np.save("/home/ubuntu/Weiyi/RFE_Feature", support)
prob = selector.predict_proba(X_test)

results = [0, 0, 0, 0, 0, 0, 0]
for cutoff in range(10, 31):
    cut = cutoff/float(100)   # Cutoff in decimal form
    y_pred = prob > cut   # If y values are greater than the cutoff
    recall = metrics.recall_score(y_test, y_pred)
    filter_rate = sum(np.logical_not(y_pred))/float(len(prob))

    if recall*6.7+filter_rate > results[0]:
        results[0] = recall*6.7+filter_rate
        results[1] = metrics.roc_auc_score(y_test, y_pred)
        results[2] = recall
        results[3] = filter_rate
        results[4] = cut
        results[5] = -5200+127000*filter_rate-850000*(1-recall)
print results
