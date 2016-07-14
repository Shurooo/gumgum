import os
import time
import multiprocessing
import numpy as np
import Sparse_Matrix_IO as smio


start = time.time()

def get_io_addr():
    root = "/mnt/rips2/2016"

    may = [(5, i) for i in range(1,8)]
    june = [(6, i) for i in range(4,26)]
    list_dates = may + june

    list_io_addr = []
    for date in list_dates:
        month = date[0]
        day = date[1]
        addr_in = os.path.join(root,
                               str(month).rjust(2, "0"),
                               str(day).rjust(2, "0"))
        list_io_addr.append(addr_in)
    return list_io_addr


def crawl(addr_day):
    print "Checking {}".format(addr_day)
    path_in = os.path.join(addr_day, "day_samp_bin.npy")
    with open(path_in, "r") as file_in:
        X = smio.load_sparse_csr(file_in)
    if len(X) != 100000:
        print "\n>>>>> Something Wrong with {}\n".format(path_in)
        exit(1)
    else:
        for i in range(len(X)):
            if len(X[i]) != 361:
                print "\n>>>>> Something Wrong with {}".format(path_in)
                print ">>>>> Line {}, wrong length {}".format(i, len(X[i]))
                exit(1)


if __name__ == '__main__':
    p = multiprocessing.Pool(8)
    list_io_addr = get_io_addr()

    for result in p.imap(crawl, list_io_addr):
        pass

    print "Completed in {} seconds\n".format(round(time.time()-start, 2))
