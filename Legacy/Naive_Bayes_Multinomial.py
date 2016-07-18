import os
import pickle
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from imblearn.over_sampling import SMOTE

# clf = MultinomialNB()
#
# root = "/home/wlu/Desktop/random_samples"
# suffix = "_num.ods"
# for i in range(5):
#     print "Generating training set {}".format(i)
#     path_in = os.path.join(root, "alldata"+str(i)+suffix)
#
#     X = []
#     with open(path_in, "r") as file_in:
#         next(file_in)
#         for line in file_in:
#             line_list = []
#             entries = line.rstrip("\r\n").split(',')
#             for item in entries:
#                 line_list.append(int(item))
#             X.append(line_list)
#
#     m = len(X[0])
#     n = len(X)
#
#     X = np.array(X)
#
#     X_train = X[:, 0:m-1]
#     y_train = X[:, m-1]
#
#     print "Done"
#     print
#
#     sm = SMOTE(ratio=0.9)
#     X_train_sm, y_train_sm = sm.fit_sample(X_train, y_train)
#
#     print
#     print "Fitting Model"
#     clf.partial_fit(X_train_sm, y_train_sm, classes=[0, 1])
#     print "Done"
#     print

with open("/home/wlu/Desktop/model_multinomial", "r") as file_in:
    clf = pickle.load(file_in)

X = []
with open("/home/wlu/Desktop/random_samples/alldata5_num.ods", "r") as file_in:
    next(file_in)
    for line in file_in:
        line_list = []
        entries = line.rstrip("\r\n").split(',')
        for item in entries:
            line_list.append(int(item))
        X.append(line_list)

m = len(X[0])
n = len(X)

X = np.array(X)

X_test = X[:, 0:m-1]
y_test = X[:, m-1]

probas = clf.predict_proba(X_test)
parametros = clf.get_params()

prediction = []
alpha = 0.95
for k in range(len(y_test)):
    if probas[k,0] > alpha:
        prediction.append(0)
    else:
        prediction.append(1)

total = len(prediction)
tn = 0
tp = 0
fp = 0
fn = 0
for i in range(total):
    if prediction[i]-y_test[i] == 0:
        if  prediction[i] == 1:
            tp+=1
        else:
            tn +=1
    else:
        if prediction[i] == 1:
            fp +=1
        else:
            fn +=1
fitering = (tn + fn) / float(total)
print 'filtering = ', fitering

print metrics.precision_recall_fscore_support(y_test, prediction, average = 'binary', beta = 12 )
print metrics.confusion_matrix(y_test,prediction)
