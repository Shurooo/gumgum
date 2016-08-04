from xgboost.sklearn import XGBClassifier
import numpy as np
from sklearn import metrics
import os
import Sparse_Matrix_IO as smio


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

clf = XGBClassifier(learning_rate =0.1,
                    n_estimators=1000,
                    max_depth=5,
                    min_child_weight=1,
                    gamma=0,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    objective= 'binary:logistic',
                    nthread=6,   # used to be 4
                    scale_pos_weight=5,   # used to be 1
                    seed=20)

print "Training"
clf.fit(X_train, y_train)
print "Done"
prob = clf.predict_proba(X_test)

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
