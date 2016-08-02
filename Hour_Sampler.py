import os
import time
import multiprocessing
import numpy as np


num = 100000
start = time.time()


def get_io_addr():
    may = [(5, i, j) for i in range(1, 8) for j in range(24)]
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
    line_indices = sorted(np.random.choice(total_line, num, replace=False))

    setoff = 0
    index = 0
    res = []
    for path_in in list_path_in:
        with open(path_in, "r") as file_in:
            for line in file_in:
                if line_indices[index]-setoff == 0:
                    res.append(line)
                    index += 1
                setoff += 1
                if index >= num:
                    break
        if index >= num:
            break

    path_out = os.path.join(addr_in, "output_raw")
    with open(path_out, "w") as file_out:
        for line in res:
            file_out.write(line)


if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr()

    for result in p.imap(crawl, list_io_addr):
        pass

    print "Completed in {} seconds\n".format(round(time.time()-start, 2))
