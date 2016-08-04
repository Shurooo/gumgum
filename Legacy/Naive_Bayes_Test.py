import os
import numpy as np
import time
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn import metrics
import pickle
import xlsxwriter
import Sparse_Matrix_IO as smio
import Get_Data as gd


__SAVE_MODEL = False
__LOAD_MODEL = False

__TRAIN_TEST_MODE = ["Next_day", "Next_week"]
__ON_OFF_LINE = ["Online"]
__SAMPLING_RATIO = [0.72]

__WEIGHT = [0.01, 0.99]

# Date Format = [(Month, Day)]
__DATA_MAY = [(5, i) for i in range(1, 8)]
__DATA_JUNE = [(6, i) for i in range(4, 26)]

__HEADER = ["Model", "Online/Offline", "Sampling", "Train", "Test", "TN", "FP", "FN", "TP", "Recall", "Filtered"]


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
        dates_pairs.append((file_train, file_test))
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


def train(addr_train, clf, ratio, onoff_line):
    X_train, y_train = gd.get(addr_train, ratio)

    if onoff_line == "Offline":
        clf.fit(X_train, y_train)
    else:
        clf.partial_fit(X_train, y_train, classes=[0, 1])

    if __SAVE_MODEL:
        model_name = "BNB_" + onoff_line + "_" + str(ratio) + "_Model"
        path_out = os.path.join(addr_train, "Naive_Bayes_Models", model_name)
        with open(path_out, "w") as file_out:
            pickle.dump(clf, file_out)

    return clf


def test(addr_test, clf):
    X_test, y_test = gd.get(addr_test)
    prediction = clf.predict(X_test)

    confusion_matrix = metrics.confusion_matrix(y_test, prediction)
    tp = confusion_matrix[1, 1]
    fp = confusion_matrix[0, 1]
    tn = confusion_matrix[0, 0]
    fn = confusion_matrix[1, 0]
    total = tp+fp+tn+fn
    recall = round(tp / float(tp+fn), 4)
    filtered = round(float(tn+fn) / total, 4)
    return [tn, fp, fn, tp], round(recall, 4), round(filtered, 4)


with open('/home/ubuntu/Weiyi/Reports/BNB_Report.xlsx', "w") as file_out:
    workbook = xlsxwriter.Workbook(file_out)
    abnormal_format = workbook.add_format()
    abnormal_format.set_bg_color("red")
    col_recall = __HEADER.index("Recall")
    col_filtered = __HEADER.index("Filtered")

    for onoff_line in __ON_OFF_LINE:
        for ratio in __SAMPLING_RATIO:
            result = ["BNB", onoff_line, ratio]

            ws = workbook.add_worksheet(onoff_line+"-"+str(ratio))
            row = 0
            ws.write_row(row, 0, __HEADER)
            row += 1

            for mode in __TRAIN_TEST_MODE:
                if mode == "Next_week":
                    row += 3
                    ws.write_row(row, 0, __HEADER)
                    row += 1

                pairs_by_month = get_addr_in(mode)

                for item in pairs_by_month:
                    clf = BernoulliNB(class_prior=__WEIGHT, alpha=0.5)

                    train_test_pairs = item[0]
                    dates_pairs = item[1]
                    for i in range(len(train_test_pairs)):
                        result_row = result[:]
                        result_row.extend([dates_pairs[i][0], dates_pairs[i][1]])

                        pair = train_test_pairs[i]
                        addr_train = pair[0]

                        model_loaded = False
                        if __LOAD_MODEL:
                            print "\n>>>>> Load Model for {}".format(addr_train)
                            model_name = "BNB" + "_" + onoff_line + "_" + str(ratio) + "_Model.p"
                            path_in = os.path.join(addr_train, "Naive_Bayes_Models", model_name)
                            try:
                                with open(path_in, "r") as file_in:
                                    clf = pickle.load(file_in)
                                model_loaded = True
                            except:
                                print ">>>>> Error: Model cannot be loaded"
                                model_loaded = False

                        if not model_loaded:
                            print "\n>>>>> Start Training on {}".format(addr_train)
                            start = time.time()
                            clf = train(addr_train, clf, ratio, onoff_line)
                            print ">>>>> Training completed in {} seconds".format(round(time.time()-start, 2))

                        addr_test = pair[1]
                        print "\n>>>>> Start Testing on {}".format(addr_test)
                        start = time.time()
                        stats, recall, filtered = test(addr_test, clf)
                        print ">>>>> Testing completed in {} seconds".format(round(time.time()-start, 2))

                        result_row.extend(stats)
                        ws.write_row(row, 0, result_row)

                        if recall < 0.95:
                            ws.write(row, col_recall, recall, abnormal_format)
                        else:
                            ws.write(row, col_recall, recall)

                        if filtered < 0.1:
                            ws.write(row, col_filtered, filtered, abnormal_format)
                        else:
                            ws.write(row, col_filtered, filtered)

                        row += 1

    workbook.close()
