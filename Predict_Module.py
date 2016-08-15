import os
import sys
import time
from sklearn import metrics
import multiprocessing


def get_io_addr(data_in):
    list_io_addr = []
    root = "/mnt/rips2/2016"
    for item in data_in:
        month = item[0]
        day = item[1]
        io_addr = os.path.join(root,
                               str(month).rjust(2, "0"),
                               str(day).rjust(2, "0"))
        addr_in = os.path.join(io_addr)
        list_io_addr.append(addr_in)
    return list_io_addr


def train(clf, data_train, sampling_ratio, sampling_mode):
    list_io_addr = get_io_addr(data_train)

    if len(list_io_addr) > 1:
        for path_in in list_io_addr:
            clf.train_online(path_in, sampling_ratio, sampling_mode)
    else:
        for path_in in list_io_addr:
            clf.train(path_in, sampling_ratio, sampling_mode)


def crawl(args):
    addr_in = args[0]
    clf = args[1]
    y_test, prediction = clf.test(addr_in)
    return metrics.confusion_matrix(y_test, prediction)


def test(clf, data_test):
    list_io_addr = get_io_addr(data_test)

    confusion_matrix = [0, 0, 0, 0]
    args = []
    for i in range(len(list_io_addr)):
        args.append((list_io_addr[i], clf))

    p = multiprocessing.Pool(4)
    for result in p.imap(crawl, args):
        confusion_matrix[0] += result[1, 1]   # tp
        confusion_matrix[1] += result[0, 1]   # fp
        confusion_matrix[2] += result[0, 0]   # tn
        confusion_matrix[3] += result[1, 0]   # fn

    tp = confusion_matrix[0]
    fp = confusion_matrix[1]
    tn = confusion_matrix[2]
    fn = confusion_matrix[3]
    total = tp+fp+tn+fn
    recall = tp / float(tp+fn)
    filtering = float(tn+fn) / total
    net_savings = 123000*filtering - 5200 - 600000*(1-recall)
    print "recall = {0:.4f}, filtering = {1:.4f}".format(round(recall, 4), round(filtering, 4))
    print "net savings = {0:.4f}".format(round(net_savings, 2))


def run(clf, data_train, data_test, sampling_ratio, sampling_mode):
    start = time.time()
    print ">>>>> Start Training"
    sys.stdout.flush()
    train(clf, data_train, sampling_ratio, sampling_mode)
    print ">>>>> Training Completed in {} seconds\n".format(round(time.time()-start, 2))

    start = time.time()
    print ">>>>> Start Testing"
    sys.stdout.flush()
    test(clf, data_test)
    print ">>>>> Testing Completed in {} seconds\n".format(round(time.time()-start, 2))
