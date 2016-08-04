import os
import operator
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn import metrics
from matplotlib import pylab as plt
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
data_train = xgb.DMatrix(X_train, label=y_train)
data_test = xgb.DMatrix(X_test, label=y_test)

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

eval_list = [(data_train,'train'), (data_test,'eval')]

num_round = 250   # Number of rounds of training, increasing this increases the range of output values
bst = xgb.train(param, data_train, num_round, verbose_eval=0)

# prob = bst.predict(data_test)
# # J score, AUC score, best recall, best filter rate, best cutoff
# results = [0, 0, 0, 0, 0, 0]
# for cutoff in range(10, 15):
#     cut = cutoff/float(100)   # Cutoff in decimal form
#     y_pred = prob > cut   # If y values are greater than the cutoff
#     recall = metrics.recall_score(y_test, y_pred)
#     filter_rate = sum(np.logical_not(y_pred))/float(len(prob))
#
#     if recall*6.7+filter_rate > results[0]:
#         results[0] = recall*6.7+filter_rate
#         results[1] = metrics.roc_auc_score(y_test, y_pred)
#         results[2] = recall
#         results[3] = filter_rate
#         results[4] = cut
#         results[5] = -5200+127000*filter_rate-850000*(1-recall)
# print results

# features = ["f" + str(i) for i in range(0, 2531)]   # Feature names are f0..f2530
# with open('xgb.fmap', 'w') as file_out:
#     for i in range(len(features)):
#         file_out.write('{0}\t{1}\tq\n'.format(i, features[i]))

# importance = bst.get_fscore(fmap='xgb.fmap')
# importance = sorted(importance.items(), key=operator.itemgetter(1), reverse=True)


# df = pd.DataFrame(importance, columns=['feature', 'fscore'])
# print 'got df = '
# print 'df[ ii fscore ii ].sum() = ', df['fscore'].sum()
# df['fscore'] = df['fscore'] / df['fscore'].sum()
# print 'got df[ ii fscore ii ]'
# plt.figure()
# df.plot()
# df.plot(kind='barh', x='feature', y='fscore', legend=False, figsize=(6, 10))
# plt.title('XGBoost Feature Importance')
# plt.xlabel('relative importance')
# plt.gcf().savefig('feature_importance_xgb.png')
