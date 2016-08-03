import os
import numpy as np
from sklearn import metrics
import xgboost as xgb
import Get_Data as gd


data = (6, 4)
root = "/mnt/rips2/2016"

month = data[0]
day = data[1]
addr_train = os.path.join(root, str(month).rjust(2, "0"), str(day).rjust(2, "0"))
addr_test = os.path.join(root, str(month).rjust(2, "0"), str(day+1).rjust(2, "0"))

X_train, y_train = gd.get(addr_train)
X_test, y_test = gd.get(addr_test)

param = {'booster': 'gbtree',   # Tree, not linear regression
         'objective': 'binary:logistic',   # Output probabilities
         'eval_metric': ['auc'],
         'bst:max_depth': 5,   # Max depth of tree
         'bst:eta': .2,   # Learning rate (usually 0.01-0.2)
         'bst:gamma': 0,   # Larger value --> more conservative
         'bst:min_child_weight': 1,
         'scale_pos_weight': 30,   # Often num_neg/num_pos
         'subsample': .8,
         'silent': 1,   # 0 outputs messages, 1 does not
         'save_period': 0,   # Only saves last model
         'nthread': 6,   # Number of cores used; otherwise, auto-detect
         'seed': 25}

data_train = xgb.DMatrix(X_train, label=y_train)
data_test = xgb.DMatrix(X_test, label=y_test)

eval_list = [(data_train,'train'), (data_test,'eval')]  # Want to train until eval error stops decreasing

num_round = 1000   # Number of rounds of training, increasing this increases the range of output values
bst = xgb.train(param,
                data_train,
                num_round,
                eval_list,
                early_stopping_rounds=10)   # If error doesn't decrease in n rounds, stop early

prediction = bst.predict(data_test)

results = [0, 0, 0, 0, 0]
for cutoff in range(0, 31):
    cut = cutoff/float(100)   # Cutoff in decimal form
    y = prediction > cut   # If y values are greater than the cutoff
    recall = metrics.recall_score(y_test, y)
    # true_negative_rate = sum(np.logical_not(np.logical_or(test_label, y)))/float(len(y_pred))
    filter_rate = sum(np.logical_not(y))/float(len(prediction))
    if recall*6.7+filter_rate > results[0]:
        results[0] = recall*6.7+filter_rate
        results[1] = metrics.roc_auc_score(y_test, y)
        results[2] = recall
        results[3] = filter_rate
        results[4] = cut
print results
