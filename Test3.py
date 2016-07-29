from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import numpy as np
from imblearn.over_sampling import SMOTE
import time
import Sparse_Matrix_IO as smio


clf = RandomForestClassifier(n_estimators=40,
                             max_features="sqrt",
                             min_weight_fraction_leaf=0.00000001,
                             oob_score=True,
                             warm_start=False,
                             n_jobs=-1,
                             random_state=1514,
                             class_weight={0:1, 1:100})
with open("/home/wlu/Desktop/day_samp_0501.npy", "r") as file_in:
    data_train = smio.load_sparse_csr(file_in)
width = np.size(data_train, 1)
X_train = data_train[:, :width-1]
y_train = data_train[:, width-1]

sm = SMOTE(ratio=0.95)
X_train, y_train = sm.fit_sample(X_train, y_train)

start = time.time()
print ">>>>> Start Training"
clf.fit(X_train, y_train)
print ">>>>> Completed in {} seconds".format(round(time.time()-start, 2))

with open("/home/wlu/Desktop/day_samp_0502.npy", "r") as file_in:
    data_test = smio.load_sparse_csr(file_in)
X_test = data_test[:, :width-1]
y_test = data_test[:, width-1]

start = time.time()
print ">>>>> Start Testing"
prediction = clf.predict(X_test)
print ">>>>> Completed in {} seconds".format(round(time.time()-start, 2))

confusion_matrix = metrics.confusion_matrix(y_test, prediction)

tp = confusion_matrix[1, 1]
fp = confusion_matrix[0, 1]
tn = confusion_matrix[0, 0]
fn = confusion_matrix[1, 0]
total = tp+fp+tn+fn
recall = round(tp / float(tp+fn), 4)
filtered = round(float(tn+fn) / total, 4)

print "recall = {}".format(recall)
print "filtered = {}".format(filtered)
