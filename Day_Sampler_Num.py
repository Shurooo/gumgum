import os
import time
import multiprocessing
from scipy.sparse import csr_matrix, vstack
import numpy as np
import Sparse_Matrix_IO as smio


num = 100000
start = time.time()

def get_io_addr():
    root = "/mnt/rips2/2016"

    may = [(5, i) for i in range(1, 2)]
    # june = [(6, i) for i in range(12, 26)]
    june = []
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
    print "Processing {}".format(addr_day)

    for suffix in ["pos", "neg"]:
        list_path_in = []
        for hour in range(0, 24):
            hour_str = str(hour).rjust(2, "0")
            list_path_in.append(os.path.join(addr_day, hour_str, "output_bin_" + suffix + ".npy"))

        total_line = 0
        for path_in in list_path_in:
            with open(path_in, "r") as file_in:
                X = smio.load_sparse_csr(file_in)
                total_line += len(X)

        line_indices = sorted(np.random.choice(total_line, num, replace=False))

        setoff = 0
        index = 0
        res = []
        for path_in in list_path_in:
            with open(path_in, "r") as file_in:
                X = smio.load_sparse_csr(file_in)
            while (index < num) and (line_indices[index]-setoff < len(X)):
                res.append(csr_matrix(X[line_indices[index]-setoff]))
                index += 1
            if index >= num:
                break
            setoff += len(X)

        path_out = os.path.join(addr_day, "day_samp_bin_" + suffix + ".npy")
        X = vstack(res)
        with open(path_out, "w") as file_out:
            smio.save_sparse_csr(file_out, X)


if __name__ == '__main__':
    p = multiprocessing.Pool(8)
    list_io_addr = get_io_addr()

    for result in p.imap(crawl, list_io_addr):
        pass

    print "Completed in {} seconds\n".format(round(time.time()-start, 2))
