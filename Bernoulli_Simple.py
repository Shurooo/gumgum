import numpy as np
import os, csv, sys, multiprocessing, warnings
from scipy.sparse import csr_matrix
from imblearn.over_sampling import SMOTE
from sklearn import metrics
from sklearn.naive_bayes import BernoulliNB
from sklearn.feature_selection import f_classif, SelectKBest


def get_data(month, day, hour=-1, mode="normal"):
    if hour != -1:
        if hour == 24:
            hour = 0
            day += 1
        addr_in = os.path.join("/mnt/rips2/2016",
                               str(month).rjust(2, "0"),
                               str(day).rjust(2, "0"),
                               str(hour).rjust(2, "0"),
                               "output_bin.npy")
    else:
        addr_in = os.path.join("/mnt/rips2/2016",
                               str(month).rjust(2, "0"),
                               str(day).rjust(2, "0"),
                               "day_samp_newer_bin.npy")
    with open(addr_in, "r") as file_in:
        loader = np.load(file_in)
        data = csr_matrix((loader['data'], loader['indices'], loader['indptr']), shape=loader['shape']).toarray()
    X = data[:, :-1]
    y = data[:, -1]

    if mode == "over":
        sm = SMOTE(ratio=0.99, verbose=0)
        X, y = sm.fit_sample(X, y)

    return X, y


def search_cut(prob, y_test):
    score = 0
    recall_best = 0
    filter_rate_best = 0
    net_savings_best = 0
    cut_best = 0
    for cutoff in range(0, 31):
        cut = cutoff/float(100)
        y_pred = prob > cut
        recall = metrics.recall_score(y_test, y_pred)
        filter_rate = sum(np.logical_not(y_pred))/float(len(prob))
        if recall*6.7+filter_rate > score:
            score = recall*6.7+filter_rate
            recall_best = recall
            filter_rate_best = filter_rate
            net_savings_best = -5200+127000*filter_rate-850000*(1-recall)
            cut_best = cut
    return score, recall_best, filter_rate_best, cut_best, net_savings_best


X, y = get_data(6, 19)
selectK = SelectKBest(f_classif, k=1000)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    selectK.fit(X, y)

for day in range(19, 20):
    # clf = BernoulliNB(class_prior=[0.1, 0.9], alpha=3218.75)
    clf = BernoulliNB(class_prior=[0.5, 0.5], alpha=0.5)
    X_train, y_train = get_data(6, day)
    X_train = selectK.transform(X_train)
    clf.fit(X_train, y_train)
    X_test, y_test = get_data(6, day+1)
    X_test = selectK.transform(X_test)
    prob = clf.predict_proba(X_test)[:, -1]
    print day, search_cut(prob, y_test)
    sys.stdout.flush()

# def crawl(day):
#     print ">>> Working on day {}".format(day)
#     clf = BernoulliNB(alpha=0.5)
#     with open("/home/ubuntu/Weiyi/Reports/BNB/BNB_{}.csv".format(day), "w") as file_out:
#         wr = csv.writer(file_out)
#         wr.writerow(["day", "hour", "score", "recall", "filter rate", "cut", "net savings"])
#         if day == 25:
#             hour_range = 23
#         else:
#             hour_range = 24
#         for hour in range(hour_range):
#             result = [day, hour]
#             sys.stdout.flush()
#             X_train, y_train = get_data(6, day, hour)
#             clf.fit(X_train, y_train)
#             # clf.partial_fit(X_train, y_train, classes=[0, 1])
#             X_test, y_test = get_data(6, day, hour+1)
#             prob = clf.predict_proba(X_test)[:, -1]
#             result.extend(search_cut(prob, y_test.toarray()))
#             wr.writerow(result)
#
#
# if __name__ == "__main__":
#     # cpus = multiprocessing.cpu_count()
#     p = multiprocessing.Pool(4)
#     day_list = range(19, 26)
#     for result in p.imap(crawl, day_list):
#         pass
