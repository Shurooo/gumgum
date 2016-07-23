import os
import time
import multiprocessing
from scipy.sparse import csr_matrix, vstack
import numpy as np
import Sparse_Matrix_IO as smio


start = time.time()

def get_io_addr():
    root = "/mnt/rips2/2016"

    # may = [(5, i, j) for i in range(1, 8) for j in range(24)]
    # june = [(6, i, j) for i in range(4, 26) for j in range(24)]
    may = [(5, 1, 00)]
    june = []
    list_dates = may + june

    list_io_addr = []
    for date in list_dates:
        month = date[0]
        day = date[1]
        hour = date[2]
        addr_in = os.path.join(root,
                               str(month).rjust(2, "0"),
                               str(day).rjust(2, "0"),
                               str(hour).rjust(2, "0"))
        list_io_addr.append(addr_in)
    return list_io_addr


def crawl(addr_in):
    print "Processing {}".format(addr_in)
    with open(addr_in, "r") as file_in:
        X = smio.load_sparse_csr(file_in)

    path_out_pos = os.path.join(addr_in, "output_bin_pos.npy")
    path_out_neg = os.path.join(addr_in, "output_bin_neg.npy")

    list_pos = []
    list_neg = []
    for line in X:
        res = line[np.size(X, 1)-1]
        if res == 1:
            list_pos.append(csr_matrix(line))
        else:
            list_neg.append(csr_matrix(line))
    X_pos = vstack(list_pos)
    X_neg = vstack(list_neg)

    file_pos = open(path_out_pos, "w")
    smio.save_sparse_csr(file_pos, X_pos)
    file_pos.close()
    file_neg = open(path_out_neg, "w")
    smio.save_sparse_csr(file_neg, X_neg)
    file_neg.close()


if __name__ == '__main__':
    p = multiprocessing.Pool(4)
    list_io_addr = get_io_addr()

    for result in p.imap(crawl, list_io_addr):
        pass

    print "Completed in {} seconds\n".format(round(time.time()-start, 2))
