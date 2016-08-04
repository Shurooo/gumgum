import os
import numpy as np
import xgboost as xgb
from sklearn import metrics
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import SelectKBest
import Sparse_Matrix_IO as smio

'''
    Feature Selection source:
    https://www.kaggle.com/sureshshanmugam/santander-customer-satisfaction/xgboost-with-feature-selection/code
    Another source to explore:
    https://www.kaggle.com/mmueller/liberty-mutual-group-property-inspection-prediction/xgb-feature-importance-python/code
    XGBoost 101 found at http://xgboost.readthedocs.io/en/latest/python/python_intro.html
'''


def get_data(month, day, hour=-1):
    root = "/home/wlu/Desktop/Data"
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

selectK = SelectKBest(f_classif, k=1000)
selectK.fit(X_train, y_train)

X_train = selectK.transform(X_train)
X_test = selectK.transform(X_test)

data_train = xgb.DMatrix(X_train, label=y_train)
data_test = xgb.DMatrix(X_test, label=y_test)

print selectK.get_support(indices=True)

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
bst = xgb.train(param, data_train, num_round, verbose_eval=0)
prob = bst.predict(data_test)

results = [0, 0, 0, 0, 0, 0]
for cutoff in range(10, 15):
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
