from imblearn.over_sampling import SMOTE
import Undersampling as US
from sklearn.utils import column_or_1d
import numpy as np
import time
from sklearn.metrics import make_scorer, fbeta_score
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn import metrics, grid_search
import Sparse_Matrix_IO as smio


__ADDR_IN = "/mnt/rips2/2016/05/01/day_samp_bin.npy"


def J_score(clf, X, y):
    y_pred = clf.predict(X)
    confusion_matrix = metrics.confusion_matrix(y, y_pred)
    tp = confusion_matrix[1, 1]
    fp = confusion_matrix[0, 1]
    tn = confusion_matrix[0, 0]
    fn = confusion_matrix[1, 0]
    total = len(y)
    recall = tp / float(tp+fn)
    filtered = float(tn) / total
    return recall + filtered / 5


def get_data(ratio, sampling):
    with open(__ADDR_IN, "r") as file_in:
        data = smio.load_sparse_csr(file_in)
    n = 30000
    if sampling == "Over":
        m = int(np.size(data, 1))
        k = int(0.8*n)
        X = data[:n, :m-1]
        y = data[:n, m-1:]
        X_train = X[:k, :]
        y_train = y[:k]
        sm = SMOTE(ratio=ratio)
        X_train, y_train = sm.fit_sample(X_train, column_or_1d(y_train, warn=False))
        X_test = X[k:, :]
        y_test = y[k:]
    else:
        data = US.undersample(data, ratio)
        m = int(np.size(data, 1))
        k = int(0.8*np.size(data, 0))
        X = data[:, :m-1]
        y = data[:, m-1:]
        X_train = X[:k, :]
        y_train = y[:k]
        X_test = X[k:, :]
        y_test = y[k:]
    return X_train, y_train, X_test, y_test


def lm():
    myfile = open("/home/ubuntu/Weiyi/GridSearch_Bern.txt", "w")

    for ratio in [0.1 + 0.1*i for i in range(9)]:
        sampling = "Under"

        myfile.write("_____________________________________________\n")
        myfile.write(sampling+"Sampling Ratio = "+str(ratio))
        myfile.write("\n")

        X, y, X_cv, y_cv = get_data(ratio, sampling)
        classes_weights = []
        step = np.arange(0.5, 0.91, 0.1)
        for i in step:
            classes_weights.append([1-i, i])
        step = np.arange(0.91, 0.991, 0.01)
        for i in step:
            classes_weights.append([1-i, i])
        step = np.arange(0.991, 1, 0.001)
        for i in step:
            classes_weights.append([1-i, i])
        parameters = {"class_prior": classes_weights, "alpha": [0.5, 1, 1.5, 2]}

        gum_score = make_scorer(fbeta_score, beta = 10)  #using f1 score
        #gum_score = make_scorer(recall_score, beta = 12)  #using recall score
        clf = grid_search.GridSearchCV(BernoulliNB(), parameters, cv=3, scoring=J_score)

        start = time.time()
        print "fitting Multinomial NBs"
        clf.fit(X, y)
        elapsed1 = time.time()-start

        myfile.write("Best parameters set found on development set: ")
        myfile.write(str(clf.best_params_))
        myfile.write("\n")

        start = time.time()
        print "predicting"
        y_pred = clf.predict(X_cv)
        elapsed2 = time.time()-start

        confusion_matrix = metrics.confusion_matrix(y_cv, y_pred)
        tp = confusion_matrix[1, 1]
        fp = confusion_matrix[0, 1]
        tn = confusion_matrix[0, 0]
        fn = confusion_matrix[1, 0]
        total = tp+fp+tn+fn
        recall = round(tp / float(tp+fn), 4)
        filtered = round(float(tn) / total, 4)

        myfile.write("Recall: \n")
        myfile.write(str(recall))
        myfile.write("\n")

        myfile.write("Filtered: \n")
        myfile.write(str(filtered))
        myfile.write("\n")

        myfile.write("Time to fit: " + str(elapsed1) + "\n")
        myfile.write("Time to predict: " + str(elapsed2) + "\n")

    myfile.close()

lm()
