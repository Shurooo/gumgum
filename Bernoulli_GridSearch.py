from imblearn.over_sampling import SMOTE
import Undersampling as US
import numpy as np
import time
from sklearn.metrics import make_scorer, fbeta_score
from sklearn.naive_bayes import BernoulliNB
from sklearn import metrics, grid_search
from scipy.sparse import csr_matrix


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
    return recall + filtered / 4


def GetData(data_list): ## Input Weiyi-formatted Data
    print "Reading Data..."
    count, temp = 1, np.load(data_list[0])
    Data = csr_matrix((  temp['data'], temp['indices'], temp['indptr']),
                         shape = temp['shape'], dtype=float).toarray()
    for i in range(1,len(data_list)):
        count +=1
        temp = np.load(data_list[i])
        temp2 = csr_matrix((temp['data'], temp['indices'], temp['indptr']),
                         shape = temp['shape'], dtype=float)
        temp3 = temp2.toarray()
        Data = np.append(Data,temp3,0)
    print "All data files read"
    return Data


def DataFormat(data_list, ratio):
    Data = GetData(data_list)
    m = int(np.size(Data,1))
    #n = int(np.size(Data,0))
    n = 30000
    Data = US.undersample(Data[:n, :], ratio)
    X = Data[:, 1:m-1]
    y = Data[:, m-1]

    k = int(0.8*n)
    
    # sm = SMOTE(ratio= ratio)
    # X_resampled, y_scaled = sm.fit_sample(X[:k,:],y[:k])
    # X_scaled = X_resampled

    X_scaled = X[:k,:]
    y_scaled = y[:k]
    X_CV = X[k:,:]
    y_CV = y[k:]

    return X_scaled, y_scaled, X_CV, y_CV


def lm(data):
    myfile = open("/home/ubuntu/Weiyi/GridSearch3.txt", "w")

    for ratio in [0.1 + 0.1*i for i in range(9)]:
        myfile.write("_____________________________________________\n")
        myfile.write("Under Sampling Ratio = "+str(ratio))
        myfile.write("\n")

        X, y, X_cv, y_cv = DataFormat(data, ratio)
        classes_weights = []
        step = np.arange(0.5,0.91,0.1)
        for i in step:
            classes_weights.append([1-i, i])
        step = np.arange(0.91,0.991,0.01)
        for i in step:
            classes_weights.append([1-i, i])
        step = np.arange(0.991,1,0.001)
        for i in step:
            classes_weights.append([1-i, i])
        parameters = {"class_prior": classes_weights, "alpha":[0.5, 1, 1.5, 2, 4, 8]}

        gum_score = make_scorer(fbeta_score, beta = 10)  #using f1 score
        #gum_score = make_scorer(recall_score, beta = 12)  #using recall score
        clf = grid_search.GridSearchCV(BernoulliNB(), parameters, cv=3, scoring=gum_score)

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

# Running the model on these data
lm(["/mnt/rips2/2016/06/04/day_samp_bin.npy"])
