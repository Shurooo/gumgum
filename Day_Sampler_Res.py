import os
import time
import multiprocessing
import numpy as np
from scipy import vstack
import Sparse_Matrix_IO as smio


def get_io_addr():
    # may = [(5, i) for i in range(1, 8)]
    may = []
    june = [(6, i) for i in range(5, 26)]
    # june = []
    list_dates = may + june
    root = "/mnt/rips2/2016"

    list_io_addr = []
    for date in list_dates:
        month = date[0]
        day = date[1]
        addr_in = os.path.join(root,
                               str(month).rjust(2, "0"),
                               str(day-1).rjust(2, "0"),
                               "day_samp_res_pos.npy")
        addr_day_out = os.path.join(root,
                                str(month).rjust(2, "0"),
                                str(day).rjust(2, "0"))
        list_io_addr.append((addr_in, addr_day_out))
    return list_io_addr


def get_data(addr_in):
    with open(addr_in, "r") as file_in:
        data = smio.load_sparse_csr(file_in)
    indices = sorted(np.random.choice(np.size(data, 0), 50000, replace=False))
    return data[indices, :]


def crawl(addr_io):
    addr_in = addr_io[0]
    addr_day_out = addr_io[1]
    print "Processing {}".format(addr_day_out)

    data_old = get_data(addr_in)
    data_new = get_data(os.path.join(addr_day_out, "day_samp_new_pos.npy"))

    data = vstack([data_old, data_new])
    np.random.shuffle(data)

    with open(os.path.join(addr_day_out, "day_samp_res_pos.npy"), "w") as file_out:
        smio.save_sparse_csr(file_out, data)


start = time.time()
list_io_addr = get_io_addr()
for addr_io in list_io_addr:
    crawl(addr_io)
print "Completed in {} seconds\n".format(round(time.time()-start, 2))
