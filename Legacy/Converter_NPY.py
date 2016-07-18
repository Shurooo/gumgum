import numpy as np
from scipy.sparse import csr_matrix
import time
import os
import Fields_and_Methods
import multiprocessing


start = time.time()


def get_io_addr_random_sample():
    list_io_addr = []
    root = "/home/ubuntu/random_samples"
    prefix = ["all", "", "new"]
    suffix = [i for i in range(6)]
    for i in prefix:
        for j in suffix:
            file_name = i+"data"+str(j)
            addr_in = os.path.join(root, file_name+"_num.ods")
            addr_out = os.path.join(root, file_name+"_bin.ods")
            list_io_addr.append((addr_in, addr_out))
    return list_io_addr


def get_io_addr():
    list_day = [i for i in range(2,3)]
    list_hour = [i for i in range(1)]
    list_month = [5]

    filename_in = "output.ods"
    filename_out = "sparse_matrix_bin.npy"

    return Fields_and_Methods.make_io_addr(list_month,
                                           list_day,
                                           list_hour,
                                           filename_in,
                                           filename_out)


def save_sparse_csr(filename, array):
    np.savez(filename,data = array.data ,indices=array.indices,
             indptr =array.indptr, shape=array.shape )


def load_sparse_csr(filename):
    loader = np.load(filename)
    return csr_matrix((  loader['data'], loader['indices'], loader['indptr']),
                         shape = loader['shape'])


def crawl(io_addr):
    addr_in = io_addr[0]
    addr_out = io_addr[1]

    my_matrix = []
    with open(addr_in, "r") as data:
        print addr_in
        next(data)
        for line in data:
            line_bin = []
            entries = line.rstrip('\r\n').split(',')
            for i in range(len(Fields_and_Methods.__INDICES)):
                line_bin.extend(binarize(entries[Fields_and_Methods.__INDICES[i]], i))
            site_cat = entries[Fields_and_Methods.__INDEX_SITE_CAT:Fields_and_Methods.__INDEX_SITE_CAT + 26]
            line_bin.extend(site_cat)
            line_bin.append(entries[Fields_and_Methods.__INDEX_BKC])
            line_bin.append(entries[Fields_and_Methods.__INDEX_RESPONSE])
            my_matrix.append(line_bin)
    my_matrix = csr_matrix(my_matrix)
    with open(addr_out, "w") as file_out:
        save_sparse_csr(file_out, my_matrix)


def binarize(value, index):
    list_bin = [0]*len(Fields_and_Methods.__CLASSES[index])
    indexing = Fields_and_Methods.__CLASSES[index][0]
    list_bin[int(value)-indexing] = 1
    return list_bin


def get_header_bin(classes):
    header_bin = []
    for i in range(len(classes)):
        for j in range(len(classes[i])):
            header_bin.append(Fields_and_Methods.__FEATURES[i] + "_" + str(classes[i][j]))
    header_bin.extend(["site_cat {}".format(i+1) for i in range(26)])
    header_bin.append("bkc")
    header_bin.append("response")
    return header_bin


if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr_random_sample()

    for result in p.imap(crawl, list_io_addr):
        pass

    print "Completed in {} seconds".format(round(time.time()-start, 2))
    print
