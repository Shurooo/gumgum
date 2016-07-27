import os
import xlsxwriter
import pickle
import numpy as np
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import Get_Data as gd


__HEADER = ["Model", "Train", "Test", "TN", "FP", "FN", "TP", "Recall", "Filtered"]


def format_addr(dates_by_month, mode):
    root = "/mnt/rips2/2016"
    train_test_pairs = []
    dates_pairs = []
    for i in range(len(dates_by_month)-mode):
        train = dates_by_month[i]
        test = dates_by_month[i+mode]
        date_train = os.path.join(str(train[0]).rjust(2, "0"), str(train[1]).rjust(2, "0"))
        date_test = os.path.join(str(test[0]).rjust(2, "0"), str(test[1]).rjust(2, "0"))
        addr_train = os.path.join(root, date_train)
        addr_test = os.path.join(root, date_test)

        train_test_pairs.append((addr_train, addr_test))
        dates_pairs.append((date_train, date_test))
    return train_test_pairs, dates_pairs


def get_addr_in(mode, data):
    pairs_by_month = []
    if mode == "Next_day":
        for dates_by_month in data:
            tuple_pairs = format_addr(dates_by_month, 1)
            pairs_by_month.append(tuple_pairs)
    else:
        tuple_pairs = format_addr(data[0], 7)
        pairs_by_month.append(tuple_pairs)
    return pairs_by_month


def train(addr_train, clf, ratio, add_estimators):
    X_train, y_train = gd.get(addr_day=addr_train, ratio=ratio, features_to_get=__FEATURES_TO_GET)

    print "Fitting Model......"
    clf.n_estimators += add_estimators
    clf.fit(X_train, y_train)
    print "Done"

    if __SAVE_MODEL:
        model_name = "RF_" + onoff_line + "_" + str(ratio) + "_Model.p"
        dir_out = os.path.join(addr_train, "Random_Forest_Models")
        if not os.path.isdir(dir_out):
            os.mkdir(dir_out)
        path_out = os.path.join(dir_out, model_name)
        with open(path_out, "w") as file_out:
            pickle.dump(clf, file_out)

    return clf


def test(addr_test, clf):
    path_in = os.path.join(addr_test, "day_samp_bin.npy")
    X_test, y_test = gd.get(addr_day=addr_test, features_to_get=__FEATURES_TO_GET)

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


def init_workbook(file_out):
    workbook = xlsxwriter.Workbook(file_out)
    abnormal_format = workbook.add_format()
    abnormal_format.set_bg_color("red")
    col_recall = __HEADER.index("Recall")
    col_filtered = __HEADER.index("Filtered")
    return workbook, abnormal_format, col_recall, col_filtered


def init_worksheet(workbook):
    ws = workbook.add_worksheet()
    ws.write_row(0, 0, __HEADER)
    return ws

def run_test(clf, model, data, train_test_mode, report_name=-1, report_root="/home/ubuntu/Weiyi/Reports"):
    if report_name == -1:
        report_name = model + "_Report.xlsx"
    file_out = open(os.path.join(report_root, report_name), "w")
    workbook, abnormal_format, col_recall, col_filtered = init_workbook(file_out)

    ws = init_worksheet(workbook)
    row = 1

    for mode in train_test_mode:
        if mode == "Next_week":
            row += 3
            ws.write_row(row, 0, __HEADER)
            row += 1

        result = [model]

        pairs_by_month = get_addr_in(data, mode)
        recall_list = []
        filtered_list = []
        for item in pairs_by_month:
            train_test_pairs = item[0]
            dates_pairs = item[1]
            for i in range(len(train_test_pairs)):
                result_row = result[:]
                result_row.extend([dates_pairs[i][0], dates_pairs[i][1]])

                pair = train_test_pairs[i]
                addr_train = pair[0]
                print "\n>>>>> Start Training on {}".format(addr_train)
                start = time.time()
                clf = train(addr_train, clf, ratio, add_estimators)
                print ">>>>> Training completed in {} seconds".format(round(time.time()-start, 2))

    workbook.close()
    file_out.close()


    for mode in train_test_mode:
        if mode == "Next_week":
            row += 3
            ws.write_row(row, 0, __HEADER)
            row += 1

                pairs_by_month = get_addr_in(mode)
                recall_list = []
                filtered_list = []
                for item in pairs_by_month:
                    clf = RandomForestClassifier(n_estimators=init_estimators,
                                                 max_features="sqrt",
                                                 oob_score=True,
                                                 warm_start=if_warm_start,
                                                 n_jobs=-1,
                                                 random_state=1514)

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
                            model_name = "RF" + "_" + onoff_line + "_" + str(ratio) + "_Model.p"
                            path_in = os.path.join(addr_train, "Random_Forest_Models", model_name)
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
                            clf = train(addr_train, clf, ratio, add_estimators)
                            print ">>>>> Training completed in {} seconds".format(round(time.time()-start, 2))

                        addr_test = pair[1]
                        print "\n>>>>> Start Testing on {}".format(addr_test)
                        start = time.time()
                        stats, recall, filtered = test(addr_test, clf)
                        print ">>>>> Testing completed in {} seconds".format(round(time.time()-start, 2))

                        recall_list.append(recall)
                        filtered_list.append(filtered)
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

                recall_avg = round(sum(recall_list) / len(recall_list), 4)
                ws.write(row, col_recall, recall_avg)

                filtered_avg = round(sum(filtered_list) / len(filtered_list), 4)
                ws.write(row, col_filtered, filtered_avg)

    workbook.close()
