import numpy as np
import time  #for the  time.sleep(sec)
from imblearn.over_sampling import SMOTE
#X = np.random.randint(5, size=(6, 100))
from sklearn import metrics


X = []
#path_in = "/home/rmendoza/Documents/Data/01/00/output.ods"
path_in = "/home/wlu/Desktop/alldata0_num.ods"
with open(path_in, "r") as file_in:
    next(file_in)
    for line in file_in:
        my_list = []
        entries = line.rstrip("\r\n").split(',')
        my_list.append(entries[0]) # DSP
        my_list.append(entries[0]) # hour
        my_list.append(entries[1]) # day
        my_list.extend(entries[2:7]) # country margin ...
        my_list.extend(entries[33:41]) # browser type ...
        X.append(my_list)
        #X.append(int(entries) for entries in str.split(' ') if entries.isdigit()
m = len(X[0]) #number of features #
print 'm = ', m
n = len(X) # number of points
print 'n = ',n
x_train_len = int(n*0.8)
print 'x_train_len = ',x_train_len

for i in range(n):
    for j in range(m):
        X[i][j] = int(X[i][j])

X = np.array(X)
print 'X[0:3] = ', X[0:3]
print 'X[0:3,m-1] = ', X[0:3,m-1]
#rangeFeatures = range(m-2)
rangeFeatures = range(0,m-2)
print 'rangeFeatures: ', rangeFeatures
X_train = X[1:x_train_len-1,rangeFeatures]
sm = SMOTE(ratio=0.75)
Xtest = X[x_train_len:n,rangeFeatures]
y_train = X[1:x_train_len-1,m-1]
Xtrain, ytrain = sm.fit_sample(X_train,y_train)
ytest = X[x_train_len:n,m-1]
print 'Xtrain: ', Xtrain[1:3]
print 'Xtest: ', Xtest[1:3]
print 'ytrain: ', ytrain[1:3]
print 'yest: ', ytest[1:3]
#print X[1]
#y = np.array([1, 2, 3, 4, 5, 6])

#check consistency of number of samples
#print len(Xtrain)
#print len(ytrain)
#time.sleep(10)

from sklearn.naive_bayes import MultinomialNB
clf = MultinomialNB()
clf.fit(Xtrain, ytrain)

#get the probabilities:
print 'PredictionProbabilities (first 10)'
probas = clf.predict_proba(Xtest)
print probas[0:10,1]
print 'Parameters: '
parametros = clf.get_params()
print parametros
my_prediction = []  # will be zero or one depending on probability
                    #       but, we will change the decision boundary
for k in range(len(ytest)):
    if probas[k,0]>0.95:
        my_prediction.append(0)
    else:
        my_prediction.append(1)
#prediction = clf.predict(Xtest) #the prediction of the non-modified Modell
prediction = my_prediction
total = len(prediction)
tn = 0
tp = 0
fp = 0
fn = 0
#print 'prediction[3]', prediction[3]
#print 'ytest[3]', ytest[3]
for i in range(total):
    if prediction[i] - ytest[i] == 0:
        if  prediction[i] == 1:
            tp+=1
        else:
            tn +=1
    else:
        if prediction[i] == 1:
            fp +=1
        else:
            fn +=1
print 'tp = ', tp
print 'tn = ', tn
print 'fp = ', fp
print 'fn = ', fn
#suma = tp + tn + fp + fn
#print 'sum = ', suma     #solo para checar que coinciden
print 'total DataPoints =', total
fitering = (tn + fn) / float(total)
print 'filtering = ', fitering
print 'precision, recall and other stuff: '
print metrics.precision_recall_fscore_support(ytest,prediction, average = 'binary', beta = 12 )
print 'Confusion matrix: '
print 'tn  fp'
print 'fn  tp'
print metrics.confusion_matrix(ytest,prediction)