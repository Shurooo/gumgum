import os
import time
import random
import multiprocessing
from scipy.sparse import csr_matrix, vstack
import Sparse_Matrix_IO as smio


num = 100000
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
    res = []
    count = 0
    print "Processing {}".format(addr_day)
    for hour in range(0,24):
        hour_str = str(hour).rjust(2, "0")
        path_in = os.path.join(addr_day, hour_str, "output.npy")
        with open(path_in, "r") as file_in:
            X = smio.load_sparse_csr(file_in)
        for line in X:
            if count < num:
                res.append(csr_matrix(line))
                count += 1
            else:
                rand = random.randint(0, count)
                if rand < num:
                    res[rand] = csr_matrix(line)

        path_out = os.path.join(addr_day, "day_samp_num.npy")
        X = vstack(res)
        with open(path_out, "w") as file_out:
            smio.save_sparse_csr(file_out, X)


if __name__ == '__main__':
    p = multiprocessing.Pool(8)
    list_io_addr = get_io_addr()

    for result in p.imap(crawl, list_io_addr):
        pass

    print "Completed in {} seconds\n".format(round(time.time()-start, 2))
