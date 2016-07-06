import time
import os
import errno
import csv
import Data_Fields
import multiprocessing
from functools import partial


start = time.time()

list_day = [i for i in range(2,3)]
list_hour = [i for i in range(1)]


def crawl(hour, day):
    p1 = str(day).rjust(2,'0')
    p2 = str(hour).rjust(2,'0')
    addr_out = make_output_addr(p1, p2)
    addr_in = os.path.join(Data_Fields.ADDR_IN_ROOT, p1, p2, "output_another.ods")

    with open(os.path.join(addr_out, "output_bin.ods"), "w") as file_out:
        wr = csv.writer(file_out, quoting = csv.QUOTE_MINIMAL)
        wr.writerow(get_header_bin(Data_Fields.__CLASSES))
        with open(addr_in, "r") as data:
            print addr_in
            next(data)
            for line in data:
                line_bin = []
                entries = line.rstrip('\r\n').split(',')
                for i in range(len(Data_Fields.__INDICES)):
                    line_bin.extend(binarize(entries[Data_Fields.__INDICES[i]], i))
                site_cat = entries[Data_Fields.__INDEX_SITE_CAT:Data_Fields.__INDEX_SITE_CAT+26]
                line_bin.extend(site_cat)
                line_bin.append(entries[Data_Fields.__INDEX_BKC])
                line_bin.append(entries[Data_Fields.__INDEX_RESPONSE])
                wr.writerow(line_bin)


def make_output_addr(p1, p2):
    out_path = os.path.join(Data_Fields.ADDR_OUT_ROOT, p1, p2)
    try:
        os.makedirs(out_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    return out_path


def binarize(value, index):
    list_bin = [0]*len(Data_Fields.__CLASSES[index])
    indexing = Data_Fields.__CLASSES[index][0]
    list_bin[int(value)-indexing] = 1
    return list_bin


def get_header_bin(classes):
    header_bin = []
    for i in range(len(classes)):
        for j in range(len(classes[i])):
            header_bin.append(Data_Fields.__FEATURES[i]+"_"+str(classes[i][j]))
    header_bin.extend(["site_cat {}".format(i+1) for i in range(26)])
    header_bin.append("bkc")
    header_bin.append("response")
    return header_bin


if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    for day in list_day:
        partial_crawl = partial(crawl, day = day)
        for result in p.imap(partial_crawl, list_hour):
            pass

    print "Completed in {} seconds".format(round(time.time()-start, 2))
    print
