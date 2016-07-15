from imblearn.over_sampling import SMOTE
import numpy as np
import time
from sklearn.naive_bayes import MultinomialNB # BernoulliNB
from sklearn import linear_model, preprocessing, metrics, grid_search
from sklearn.metrics import make_scorer, recall_score, fbeta_score
from scipy.sparse import csr_matrix


#def J_score(y,y_pred):
#    r = metrics.recall_score(y,y_pred, average='binary')
#    n = len(y)
#    TN_rate = (n-np.count_nonzero(y+y_pred+2*np.ones(n)))/n
#    return r+TN_rate/5

def GetData(data_list): ## Input Weiyi-formatted Data
    print "Reading Data..."
    count, temp = 1, np.load(data_list[0])
    Data = csr_matrix((  temp['data'], temp['indices'], temp['indptr']),
                         shape = temp['shape'], dtype=float).toarray()
    print "Finished reading data file %s of %s..." %(count, len(data_list))
    for i in range(1,len(data_list)):
        count +=1
        temp = np.load(data_list[i])
        temp2 = csr_matrix((temp['data'], temp['indices'], temp['indptr']),
                         shape = temp['shape'], dtype=float)
        temp3 = temp2.toarray()
        Data = np.append(Data,temp3,0)
        print "Finished reading data file %s of %s..." %(count, len(data_list))
    print "All data files read"
    return Data


def DataFormat(data_list):
    Data = GetData(data_list)
    m = int(np.size(Data,1))
    #n = int(np.size(Data,0))
    n = 30000
    print "The number of data points is %s, each with %s features" % (n, m-2)
    print "Creating X,y"
    X = Data[:n,1:m-1]
    y = Data[:n,m-1]
    print "X,y created"
    print "Formatting ..."
    k = int(0.8*n)
    sm = SMOTE(ratio= 0.75)
    X_resampled, y_scaled = sm.fit_sample(X[:k,:],y[:k])
    #X_scaled = preprocessing.scale(X_resampled)
    X_scaled = X_resampled
    print "Training set size is %s" % np.size(y_scaled)
    X_CV = X[k:,:]
    y_CV = y[k:]
    #X_CV, y_CV = preprocessing.scale(X[k:,:]), y[k:]
    print "Formatted"
    return X_scaled, y_scaled, X_CV, y_CV


def lm(data):
    X, y, X_cv, y_cv = DataFormat(data)
    classes_weights = []
    steppingi = np.arange(0.5,0.91,0.1)
    for i in steppingi:
        classes_weights.append([1-i, i])
    steppingi = np.arange(0.91,0.991,0.01)
    for i in steppingi:
        classes_weights.append([1-i, i])
    steppingi = np.arange(0.991,1,0.001)
    for i in steppingi:
        classes_weights.append([1-i, i])
    parameters = {'class_prior': classes_weights}

    gum_score = make_scorer(fbeta_score, beta = 12)  #using f1 score
    #gum_score = make_scorer(recall_score, beta = 12)  #using recall score

    clf = grid_search.GridSearchCV(MultinomialNB(), parameters, cv=3, scoring=gum_score)

    start = time.time()
    print "fitting Multinomial NBs"
    clf.fit(X, y)
    elapsed1 = time.time()-start

    with open("/home/Weiyi/GridSearch3.txt", "w+") as myfile:
        myfile.write("Best parameters set found on development set: ")
        myfile.write(str(clf.best_params_))
        myfile.write("\n")
        myfile.write("Grid scores on development set:\n")
        for params, mean_score, scores in clf.grid_scores_:
            myfile.write("%0.3f (+/-%0.03f) for %r \n" % (mean_score, scores.std() * 2, params))
        start = time.time()

        print "predicting"
        y_pred = clf.predict(X_cv)
        elapsed2 = time.time()-start

        myfile.write("F_12 score: \n")
        myfile.write(str(fbeta_score(y_cv, y_pred, beta=12)))
        myfile.write("\n")

        myfile.write("Recall: \n")
        myfile.write(str(metrics.recall_score(y_cv, y_pred, average='binary')))
        myfile.write("\n")

        myfile.write("Confusion Matrix: \n")
        for item in metrics.confusion_matrix(y_cv, y_pred):
            myfile.write("%s\n" % item)

        myfile.write("Time to fit: " + str(elapsed1) + "\n")
        myfile.write("Time to predict: " + str(elapsed2))

# Running the model on these data
lm(["/home/kbhalla/Desktop/Data/alldata0_num.npy"])
