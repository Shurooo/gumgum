import os
import sys
import xlsxwriter
import time
from sklearn import metrics


__HEADER = ["Model", "Train", "Test", "TN", "FP", "FN", "TP", "Recall", "Filtered", "Net Savings"]


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
        print "I'm Here"
        sys.stdout.flush()
        for dates_by_month in data:
            tuple_pairs = format_addr(dates_by_month, 1)
            pairs_by_month.append(tuple_pairs)
    else:
        tuple_pairs = format_addr(data[0], 7)
        pairs_by_month.append(tuple_pairs)
    return pairs_by_month


def test(addr_test, clf):
    y_test, prediction = clf.test(addr_test)
    confusion_matrix = metrics.confusion_matrix(y_test, prediction)

    tp = confusion_matrix[1, 1]
    fp = confusion_matrix[0, 1]
    tn = confusion_matrix[0, 0]
    fn = confusion_matrix[1, 0]
    total = tp+fp+tn+fn
    recall = round(tp / float(tp+fn), 4)
    filtered = round(float(tn+fn) / total, 4)
    net_savings = round(127000*filtered - 5200 - 850000*(1-recall), 2)

    return [tn, fp, fn, tp], recall, filtered, net_savings


def init_workbook(file_out):
    workbook = xlsxwriter.Workbook(file_out)
    abnormal_format = workbook.add_format()
    abnormal_format.set_bg_color("red")
    col_recall = __HEADER.index("Recall")
    return workbook, abnormal_format, col_recall


def init_worksheet(workbook, param):
    ws = workbook.add_worksheet()
    ws.write_row(0, 0, __HEADER)
    ws.write_column(1, len(__HEADER)+1, param)
    return ws


def run(clf, model, data, sampling_ratio, sampling_mode, train_test_mode, on_off_line, param, report_name, report_root):
    if report_name == -1:
        report_name = model + "_Report.xlsx"
    file_out = open(os.path.join(report_root, report_name), "w")
    workbook, abnormal_format, col_recall= init_workbook(file_out)

    ws = init_worksheet(workbook, param)
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
        net_savings_list = []
        for item in pairs_by_month:
            train_test_pairs = item[0]
            dates_pairs = item[1]
            for i in range(len(train_test_pairs)):
                result_row = result[:]
                result_row.extend([dates_pairs[i][0], dates_pairs[i][1]])

                pair = train_test_pairs[i]
                addr_train = pair[0]
                print "\n>>>>> Start Training on {}".format(addr_train)
                sys.stdout.flush()
                start = time.time()
                if on_off_line == "Online":
                    clf.train_online(addr_train, sampling_ratio, sampling_mode)
                else:
                    clf.train(addr_train, sampling_ratio)
                print ">>>>> Training completed in {} seconds".format(round(time.time()-start, 2))
                sys.stdout.flush()

                addr_test = pair[1]
                print "\n>>>>> Start Testing on {}".format(addr_test)
                sys.stdout.flush()
                start = time.time()
                stats, recall, filtered, net_savings = test(addr_test, clf)
                print ">>>>> Testing completed in {} seconds".format(round(time.time()-start, 2))
                sys.stdout.flush()

                recall_list.append(recall)
                filtered_list.append(filtered)
                net_savings_list.append(net_savings)
                result_row.extend(stats)
                ws.write_row(row, 0, result_row)

                write_format_check(ws, row, col_recall, recall, 0.95, abnormal_format)
                write_format_check(ws, row, col_recall+1, filtered, 0.1, abnormal_format)
                write_format_check(ws, row, col_recall+2, net_savings, 0, abnormal_format)

                row += 1

        recall_avg = round(sum(recall_list) / len(recall_list), 4)
        write_format_check(ws, row, col_recall, recall_avg, 0.95, abnormal_format)

        filtered_avg = round(sum(filtered_list) / len(filtered_list), 4)
        write_format_check(ws, row, col_recall+1, filtered_avg, 0.1, abnormal_format)

        net_savings_avg = round(sum(net_savings_list) / len(net_savings_list), 4)
        write_format_check(ws, row, col_recall+2, net_savings_avg, 0, abnormal_format)

    workbook.close()
    file_out.close()


def write_format_check(ws, row, col, item, thres, abnormal_format):
    if item < thres:
        ws.write(row, col, item, abnormal_format)
    else:
        ws.write(row, col, item)
