import os
import sys
import time
import numpy as np
import operator
import Sparse_Matrix_IO as smio
import xgboost as xgb


def get_data(month, day):
    root = "/home/wlu/Desktop/Data"
    file_name = "day_samp_new_" + str(month).rjust(2, "0") + str(day).rjust(2, "0") + ".npy"
    addr_in = os.path.join(root, file_name)

    with open(addr_in, "r") as file_in:
        data = smio.load_sparse_csr(file_in)
    X = data[:, :-1]
    y = data[:, -1]
    return X, y


def create_feature_map(features, feature_imp):
    outfile = open('xgb.fmap', 'w')
    for i in range(len(features)):
        outfile.write('{0}\t{1}\tq\n'.format(i, features[i]))
        feature_imp.append([])
    outfile.close()


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

features = ["f" + str(i) for i in range(0, 2531)]   # Feature names are f0..f2530
feature_imp = []
create_feature_map(features, feature_imp)

for data in [(6, i) for i in range(4, 25)]:
    X_train, y_train = get_data(data[0], data[1])
    X_test, y_test = get_data(data[0], data[1]+1)

    data_train = xgb.DMatrix(X_train, label=y_train)
    data_test = xgb.DMatrix(X_test, label=y_test)

    eval_list = [(data_train,'train'), (data_test,'eval')]  # Want to train until eval error stops decreasing

    num_round = 1000   # Number of rounds of training, increasing this increases the range of output values
    start = time.time()
    print ">>>>> Fitting Model on {}".format(data)
    sys.stdout.flush()
    bst = xgb.train(param,
                    data_train,
                    num_round,
                    eval_list,
                    verbose_eval=0,
                    early_stopping_rounds=10)   # If error doesn't decrease in n rounds, stop early
    print ">>>>> Completed in {} seconds\n".format(round(time.time()-start, 2))

    feature_imp_bitmap = [0]*2531
    for item in bst.get_fscore(fmap='xgb.fmap').iteritems():
        index = int(item[0][1:])
        feature_imp_bitmap[index] = 1
        feature_imp[index].append(item[1])
    for i in range(len(feature_imp)):
        if feature_imp_bitmap[i] == 0:
            feature_imp[i].append(0)

feature_imp = np.array(feature_imp)
np.save("/home/wlu/Desktop/feature_imp_XGB", feature_imp)
