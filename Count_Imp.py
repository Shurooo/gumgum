import time
import os
import csv
import multiprocessing


start = time.time()

__HEADER = ["hour", "day", "country", "margin", "tmax", "bkc", "site_typeid", "browser_type",
             "bidder_id", "vertical_id", "bid_floor", "format", "product", "banner", "response"]
__INDEX_SITE_TYPE = __HEADER.index("site_typeid")
__HEADER[__INDEX_SITE_TYPE+1:1] = ["site_cat {}".format(i+1) for i in range(26)]
__DSP_INDEX = __HEADER.index("bidder_id")

with open("io_addr_root.txt", "r") as file_addr_root:
    __ADDR_ROOT = file_addr_root.readline().replace("\"", "").rstrip("\n")


def get_io_addr():
    list_day = [i for i in range(1, 8)]
    list_hour = [i for i in range(24)]
    list_month = [5, 6]

    filename_in = "output.ods"

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
            entries = line.rstrip("\r\n").split(",")
            entries.pop(__DSP_INDEX)
            entries.pop(len(entries)-1)
            str_entry = ""
            for i in entries:
                str_entry += i
            set_imp.add(str_entry)
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
