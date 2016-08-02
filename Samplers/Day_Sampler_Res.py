import os
import sys
import time
import numpy as np
from scipy import vstack
from shutil import copyfile
import Sparse_Matrix_IO as smio


new_data_ratio = 75
mode = "neg"

new_line = 1000 * new_data_ratio
if mode == "normal":
    folder = "Reservoir_Data"
    file_res = "day_samp_res_{}.npy".format(new_data_ratio)
    file_new = "day_samp_new.npy"
else:
    folder = "PosNeg/Reservoir_Data"
    file_res = "day_samp_res_{}_{}.npy".format(mode, new_data_ratio)
    file_new = "PosNeg/day_samp_new_{}.npy".format(mode)


def get_io_addr():
    # may = [(5, i) for i in range(1, 8)]
    may = []
    june = [(6, i) for i in range(4, 26)]
    # june = []
    list_dates = may + june
    root = "/mnt/rips2/2016"

    process_first_day(list_dates.pop(0), root)

    list_io_addr = []
    for date in list_dates:
        month = date[0]
        day = date[1]

        addr_in = os.path.join(root,
                               str(month).rjust(2, "0"),
                               str(day-1).rjust(2, "0"),
                               folder,
                               file_res)
        addr_day_out = os.path.join(root,
                                    str(month).rjust(2, "0"),
                                    str(day).rjust(2, "0"))
        list_io_addr.append((addr_in, addr_day_out))
    return list_io_addr


def process_first_day(date, root):
    month = date[0]
    day = date[1]
    addr_io = os.path.join(root, str(month).rjust(2, "0"), str(day).rjust(2, "0"))
    addr_in = os.path.join(addr_io, file_new)
    addr_out = os.path.join(addr_io, folder, file_res)
    copyfile(addr_in, addr_out)


def get_data(addr_in, n):
    with open(addr_in, "r") as file_in:
        data = smio.load_sparse_csr(file_in)
    indices = sorted(np.random.choice(np.size(data, 0), n, replace=False))
    return data[indices, :]


def crawl(addr_io):
    addr_in = addr_io[0]
    addr_day_out = addr_io[1]
    print "Processing {}".format(addr_day_out)
    sys.stdout.flush()

    data_old = get_data(addr_in, 100000-new_line)
    data_new = get_data(os.path.join(addr_day_out, file_new), new_line)

    data = vstack([data_old, data_new])
    np.random.shuffle(data)

    with open(os.path.join(addr_day_out, folder, file_res), "w") as file_out:
        smio.save_sparse_csr(file_out, data)


start = time.time()
list_io_addr = get_io_addr()
for addr_io in list_io_addr:
    crawl(addr_io)
print "Completed in {} seconds\n".format(round(time.time()-start, 2))
sys.stdout.flush()
