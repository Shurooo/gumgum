# import os
# import json
# import multiprocessing
#
#
# root = "/mnt/rips2/2016"
#
#
# def crawl(date):
#     print "Processing {}".format(date)
#     day = date[0]
#     hour = date[1]
#     addr = os.path.join(root,
#                         str(6).rjust(2, "0"),
#                         str(day).rjust(2, "0"),
#                         str(hour).rjust(2, "0"))
#
#     count = 0
#     for suffix in ["pos", "neg"]:
#         with open(os.path.join(addr, "output_"+suffix), "r") as file_in:
#             entries = list(file_in)
#             count += len(entries)
#
#     return hour, count
#
#
# if __name__ == '__main__':
#     date = [(i, j) for i in range(4, 26) for j in range(24)]
#     cpus = multiprocessing.cpu_count()
#     p = multiprocessing.Pool(cpus)
#
#     imp_count = [0]*24
#     for result in p.imap(crawl, date):
#         imp_count[result[0]] += result[1]
#
#     with open("/home/ubuntu/Weiyi/hourly_imp_count.json", "w") as file_out:
#         json.dump(imp_count, file_out)


import os
import time
import multiprocessing
from random import shuffle
import numpy as np


num = 50000
start = time.time()


def get_io_addr():
    # may = [(5, i, j) for i in range(1, 32) for j in range(24)]
    may = []
    june = [(6, i, j) for i in range(5, 19) for j in range(24)]
    # june = []
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

    with open(os.path.join(addr_in, "output_neg"), "r") as file_in:
        data = list(file_in)

    shuffle(data)
    total_line = len(data)

    if total_line > num:
        data_new = []
        line_indices = sorted(np.random.choice(total_line, num, replace=False))
        for index in line_indices:
            data_new.append(data[index])
        data = data_new

    path_out = os.path.join(addr_in, "output_neg_raw")
    with open(path_out, "w") as file_out:
        for line in data:
            file_out.write(line)


if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr()

    for result in p.imap(crawl, list_io_addr):
        pass

    print "Completed in {} seconds\n".format(round(time.time()-start, 2))
