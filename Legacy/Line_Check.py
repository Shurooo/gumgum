import numpy as np
import os
import multiprocessing
import Sparse_Matrix_IO


def get_io_addr():
    list_day = [i for i in range(1,8)]
    list_hour = [i for i in range(24)]
    list_month = [5,6]

    filename_in = "output_bin_new.npy"

    list_io_addr = []
    for month in list_month:
        for day in list_day:
            if month == 6:
                day += 18
            for hour in list_hour:
                addr_in = os.path.join("/mnt/rips/2016",
                                       str(month).rjust(2, "0"),
                                       str(day).rjust(2, "0"),
                                       str(hour).rjust(2, "0"),
                                       filename_in)
                list_io_addr.append(addr_in)
    return list_io_addr


def crawl(addr_in):
    print "Checking {}".format(addr_in)
    with open(addr_in, "r") as file_in:
        X = Sparse_Matrix_IO.load_sparse_csr(file_in)
    for line in X:
        if len(line) != 361:
            print "\nSomething Wrong!"
            print "File name {}\n".format(addr_in)
            exit(1)


if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr()
    for result in p.imap(crawl, list_io_addr):
        pass
