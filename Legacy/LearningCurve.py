import numpy as np
from random import shuffle
from sklearn.ensemble import RandomForestClassifier
from sklearn import linear_model, preprocessing, learning_curve, metrics
from sklearn.metrics import make_scorer, fbeta_score
import Sparse_Matrix_IO as smio
from imblearn.over_sampling import SMOTE

import matplotlib.pyplot as plt
try:
    import cPickle as pickle
except:
    import pickle


def DataFormat(data):
    Data = smio.load_sparse_csr(data)
    m = int(np.size(Data, 1))
    n = int(np.size(Data, 0))
    X_train = Data[:50000, :m-1]
    y_train = Data[:50000, m-1]
    sm = SMOTE(ratio=0.95)
    X_train, y_train = sm.fit_sample(X_train, y_train)

    data_new = []
    for i in range(np.size(X_train, 0)):
        row = list(X_train[i].tolist())
        row.append(y_train[i])
        data_new.append(row)
    shuffle(data_new)
    data_new = np.array(data_new)
    m = int(np.size(data_new, 1))
    X_train = data_new[:, :m-1]
    y_train = data_new[:, m-1]

    K = np.count_nonzero(y_train)   # Number of good data points
    return X_train, y_train, n, K   # Training set plus some numbers useful for weighting


def Learning_curve(data):
    X_train, y_train, n, K = DataFormat(data)
    clf = RandomForestClassifier(n_estimators=75,
                                 max_features=15,
                                 min_weight_fraction_leaf=0.000025,
                                 oob_score=True,
                                 warm_start=False,
                                 n_jobs=-1,
                                 random_state=1514,
                                 class_weight={0:1, 1:8})
    print "Training ... "
    plt.figure()
    plt.title("RF Learning curve")
    plt.xlabel("Training examples")
    plt.ylabel("Recall_Score")
    gum_score = make_scorer(fbeta_score, beta = 11)
    train_sizes, train_scores, test_scores = learning_curve.learning_curve(clf,
                                                                           X_train,
                                                                           y_train,
                                                                           n_jobs=-1,
                                                                           train_sizes=np.linspace(0.01, 1.0, 11),
                                                                           scoring=gum_score)
                                                                           # scoring=metrics.make_scorer(metrics.recall_score)
    print "Training complete."
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    print "Plotting..."
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.3,
                     color="b")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.3, color="#f2b518")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="b",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="#f2b518",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt


Learning_curve("/home/wlu/Desktop/random_samples/alldata0_bin.npy").show()
