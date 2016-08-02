import os
import time
import multiprocessing
from random import shuffle
import numpy as np


num = 100000
start = time.time()


def get_io_addr():
    may = [(5, i, j) for i in range(1, 2) for j in range(0)]
    # may = []
    # june = [(6, i) for i in range(4, 26)]
    june = []
    list_dates = may + june
    root = "/mnt/rips2/2016"

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

    list_path_in = []
    total_line = 0
    for suffix in ["pos", "neg"]:
        path_in = os.path.join(addr_in, "output_" + suffix)
        list_path_in.append(path_in)
        with open(path_in, "r") as file_in:
            line_count = 0
            for line in file_in:
                line_count += 1
            total_line += line_count
    with open(list_path_in[0]) as file_in:
        data = list(file_in)
    with open(list_path_in[1]) as file_in:
        data.extend(list(file_in))

    line_to_discard = total_line-num
    if line_to_discard > 0:
        line_indices = sorted(np.random.choice(line_to_discard, total_line, replace=False))
        setoff = 0
        for index in line_indices:
            del data[index-setoff]
            setoff += 1

    shuffle(data)
    path_out = os.path.join(addr_in, "output_raw")
    with open(path_out, "w") as file_out:
        for line in shuffle:
            file_out.write(line)


if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr()

    for result in p.imap(crawl, list_io_addr):
        pass

    print "Completed in {} seconds\n".format(round(time.time()-start, 2))
