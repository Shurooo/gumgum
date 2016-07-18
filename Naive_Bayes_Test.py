import os
import numpy as np
import time
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn import metrics
from imblearn.over_sampling import SMOTE
import Undersampling as US
import pickle
import csv
import Sparse_Matrix_IO as smio


__SAVE_MODEL = False
__LOAD_MODEL = False 

__MODEL = ["Bern"]
__TRAIN_TEST_MODE = ["Next_day", "Next_week"]
__ON_OFF_LINE = ["Online"]
__SAMPLING_METHOD = ["Under"]

__FEATURES = ["hour", "day", "country", "margin", "tmax", "bkc", "site_typeid", "site_cat", "browser_type",
             "bidder_id", "vertical_id", "bid_floor", "format", "product", "banner", "response"]
__FEATURES_TO_DROP = []

__RATIO_OVER = 0.95
__RATIO_UNDER = 0.3
__WEIGHT_NONE = [0.05, 0.95]
__WEIGHT_OVER = [0.01, 0.99]
__WEIGHT_UNDER = [0.05, 0.95]

# Date Format = [(Month, Day)]
__DATA_MAY = [(5, i) for i in range(1, 8)]
__DATA_JUNE = [(6, i) for i in range(4, 26)]


def discard_vars(X, cutoffs):
    X_new = []
    for line in X:
        new_line = []
        for i in range(0, len(cutoffs), 2):
            new_line.extend(line[cutoffs[i]:cutoffs[i+1]])
        X_new.append(new_line)
    return np.array(X_new)


def format_addr(dates, mode):
    root = "/mnt/rips2/2016"
    train_test_pairs = []
    dates_pairs = []
    for i in range(len(dates)-mode):
        train = dates[i]
        test = dates[i+mode]
        file_train = os.path.join(str(train[0]).rjust(2, "0"), str(train[1]).rjust(2, "0"))
        file_test = os.path.join(str(test[0]).rjust(2, "0"), str(test[1]).rjust(2, "0"))
        addr_train = os.path.join(root, file_train)
        addr_test = os.path.join(root, file_test)

        train_test_pairs.append((addr_train, addr_test))
        dates_pairs.append(file_train+"~"+file_test)
    return train_test_pairs, dates_pairs


def get_addr_in(mode):
    pairs_by_month = []
    if mode == "Next_day":
        for dates in [__DATA_MAY, __DATA_JUNE]:
            tuple_pairs = format_addr(dates, 1)
            pairs_by_month.append(tuple_pairs)
    else:
        tuple_pairs = format_addr(__DATA_JUNE, 7)
        pairs_by_month.append(tuple_pairs)
    return pairs_by_month


def get_file_name(model):
    if model == "Bern":
        return "day_samp_bin.npy"
    else:
        return "day_samp_num.npy"


def train(addr_train, clf, model, sampling, onoff_line, cutoffs):
    file_name = get_file_name(model)
    path_in = os.path.join(addr_train, file_name)
    with open(path_in, "r") as file_in:
        X = smio.load_sparse_csr(file_in)

    if len(cutoffs) > 0:
        print "Discarding selected features......"
        X = discard_vars(X, cutoffs)

    vector_len = len(X[0])
    X_train = X[:, 0:vector_len-1]
    y_train = X[:, vector_len-1]

    if sampling == "Over":
        sm = SMOTE(ratio=__RATIO_OVER)
        X_train, y_train = sm.fit_sample(X_train, y_train)
    elif sampling == "Under":
        X = US.undersample(X, __RATIO_UNDER)
        vector_len = len(X[0])
        X_train = X[:, 0:vector_len-1]
        y_train = X[:, vector_len-1].ravel()

    if onoff_line == "Offline":
        clf.fit(X_train, y_train)
    else:
        clf.partial_fit(X_train, y_train, classes=[0,1])

    if __SAVE_MODEL:
        model_name = model + "_" + onoff_line + "_" + sampling + "_Model"
        path_out = os.path.join(addr_train, "Naive_Bayes_Models", model_name)
        with open(path_out, "w") as file_out:
            pickle.dump(clf, file_out)

    return clf


def test(addr_test, clf, model, cutoffs):
    file_name = get_file_name(model)
    path_in = os.path.join(addr_test, file_name)
    with open(path_in, "r") as file_in:
        X = smio.load_sparse_csr(file_in)

    if len(cutoffs) > 0:
        print "Discarding selected features......"
        X = discard_vars(X, cutoffs)

    vector_len = len(X[0])
    X_test = X[:, 0:vector_len-1]
    y_test = X[:, vector_len-1]

    prediction = clf.predict(X_test)

    confusion_matrix = metrics.confusion_matrix(y_test, prediction)

    tp = confusion_matrix[1, 1]
    fp = confusion_matrix[0, 1]
    tn = confusion_matrix[0, 0]
    fn = confusion_matrix[1, 0]
    total = tp+fp+tn+fn
    recall = round(tp / float(tp+fn), 4)
    filtered = round(float(tn+fn) / total, 4)
    return [tn, fp, fn, tp, recall, filtered]


def get_feature_indices():
    get_feature_length = {
        "hour": 24,
        "day": 7,
        "country": 193,
        "margin": 5,
        "tmax": 4,
        "bkc": 1,
        "site_typeid": 3,
        "site_cat": 26,
        "browser_type": 9,
        "bidder_id": 35,
        "vertical_id": 16,
        "bid_floor": 6,
        "format": 20,
        "product": 6,
        "banner": 5,
        "response": 1
    }
    feature_indices = {}
    begin = 0
    end = 0
    for item in __FEATURES:
        length = get_feature_length[item]
        end += length
        feature_indices.update({item:(begin, end)})
        begin += length
    return feature_indices, end


def get_cutoffs():
    feature_indices, total_length = get_feature_indices()
    cutoffs = [0, total_length]
    for item in __FEATURES_TO_DROP:
        indices = feature_indices[item]
        cutoffs.append(indices[0])
        cutoffs.append(indices[1])

    return sorted(cutoffs)


if len(__FEATURES_TO_DROP) > 0:
    cutoffs = get_cutoffs()
else:
    cutoffs = []


def get_clf(model, class_weight):
    if model == "Bern":
        return BernoulliNB(class_prior=class_weight, alpha=0.5)
    else:
        return MultinomialNB(class_prior=class_weight, alpha=0.5)


def init_clf(model, sampling):
    class_weight_options = {
        "None": __WEIGHT_NONE,
        "Over": __WEIGHT_OVER,
        "Under": __WEIGHT_UNDER
    }
    clf = get_clf(model, class_weight_options[sampling])
    param_options = {
        "None": (clf, "cp={}".format(str(__WEIGHT_NONE).replace(",", ""))),
        "Over": (clf, "cp={}; ratio={}".format(str(__WEIGHT_OVER).replace(",", ""), __RATIO_OVER)),
        "Under": (clf, "cp={}; ratio={}".format(str(__WEIGHT_UNDER).replace(",", ""), __RATIO_UNDER))
    }
    return param_options[sampling]


with open("/home/ubuntu/Weiyi/report.csv", "w") as file_out:
    wr = csv.writer(file_out, quoting = csv.QUOTE_MINIMAL)
    wr.writerow(["Model", "Online/Offline", "Sampling", "Train~Test", "TN", "FP", "FN", "TP", "Recall", "Filtered", "Parameters"])

    for model in __MODEL:
        for mode in __TRAIN_TEST_MODE:
            pairs_by_month = get_addr_in(mode)

            for item in pairs_by_month:
                train_test_pairs = item[0]
                dates_pairs = item[1]

                result = [model]
                for onoff_line in __ON_OFF_LINE:
                    result_onoff = result[:]
                    result_onoff.append(onoff_line)

                    for sampling in __SAMPLING_METHOD:
                        result_sampling = result_onoff[:]
                        result_sampling.append(sampling)
                        clf, param = init_clf(model, sampling)

                        for i in range(len(train_test_pairs)):
                            pair = train_test_pairs[i]
                            result_final = result_sampling[:]
                            result_final.append(dates_pairs[i])
                            if onoff_line == "Offline":
                                clf, param = init_clf(model, sampling)

                            addr_train = pair[0]
                            model_loaded = False
                            if __LOAD_MODEL:
                                print "\n>>>>> Load Model for {}".format(addr_train)
                                model_name = model + "_" + onoff_line + "_" + sampling + "_Model"
                                path_in = os.path.join(addr_train, "Naive_Bayes_Models", model_name)
                                try: 
                                    with open(path_in, "r") as file_in:
                                        clf = pickle.load(file_in)
                                    model_loaded = True
                                except:
                                    print ">>>>> Error: Model cannot be loaded"
                                    model_loaded = False

                            if len(__FEATURES_TO_DROP) > 0:
                                cutoffs = get_cutoffs()
                            else:
                                cutoffs = []

                            if not model_loaded:
                                print "\n>>>>> Start Training on {}".format(addr_train)
                                start = time.time()
                                clf = train(addr_train, clf, model, sampling, onoff_line, cutoffs)
                                print ">>>>> Training completed in {} seconds".format(round(time.time()-start, 2))

                            addr_test = pair[1]
                            print "\n>>>>> Start Testing on {}".format(addr_test)
                            start = time.time()
                            stats = test(addr_test, clf, model, cutoffs)
                            print ">>>>> Testing completed in {} seconds".format(round(time.time()-start, 2))

                            result_final.extend(stats)
                            result_final.append(param)
                            wr.writerow(result_final)
