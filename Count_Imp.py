import time
import os
import csv
import multiprocessing


start = time.time()

with open("io_addr_root.txt", "r") as file_addr_root:
    __ADDR_ROOT = file_addr_root.readline().replace("\"", "").rstrip("\n")


def get_io_addr():
    list_day = [i for i in range(2,3)]
    list_hour = [i for i in range(1)]
    list_month = [5]

    filename_in = "output_bin.ods"

    list_io_addr = []
    for month in list_month:
        for day in list_day:
            if month == 6:
                day += 18
            for hour in list_hour:
                io_addr = os.path.join(__ADDR_ROOT,
                                       str(month).rjust(2, "0"),
                                       str(day).rjust(2, "0"),
                                       str(hour).rjust(2, "0"))
                list_io_addr.append(os.path.join(io_addr, filename_in))
    return list_io_addr


def crawl(io_addr):
    set_imp = set()
    with open(io_addr, "r") as file_in:
        print io_addr
        next(file_in)
        for line in file_in:
            entry = line.rstrip("\r\n").replace(",", "").replace(" ", "")
            set_imp.add(entry)
    return set_imp

if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr()

    set_imp = set()
    for result in p.imap(crawl, list_io_addr):
        set_imp = set_imp.union(result)

    print "{} distinct impressions recorded".format(len(set_imp))

    print "Completed in {} seconds".format(round(time.time()-start, 2))
    print