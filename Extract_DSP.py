import time
import os
import csv
import multiprocessing


start = time.time()

with open("io_addr_root.txt", "r") as file_addr_root:
    __ADDR_ROOT = file_addr_root.readline().replace("\"", "").rstrip("\n")

__HEADER = ["hour", "day", "country", "margin", "tmax", "bkc", "site_typeid", "browser_type",
             "bidder_id", "vertical_id", "bid_floor", "format", "product", "banner", "response"]
__INDEX_SITE_TYPE = __HEADER.index("site_typeid")
__HEADER[__INDEX_SITE_TYPE+1:1] = ["site_cat {}".format(i+1) for i in range(26)]

__INDEX_DSP = __HEADER.index("bidder_id")

__HEADER.remove("bidder_id")


def get_io_addr():
    list_io_addr = []
    root = "/home/ubuntu/random_samples"
    suffix = [i for i in range(6)]
    for j in suffix:
        file_name = "alldata"+str(j)
        addr_in = os.path.join(root, file_name+"_num.ods")
        list_io_addr.append((addr_in, file_name))
    return list_io_addr


def crawl(io_addr):
    root_out = "/home/ubuntu/Weiyi/DSPs"
    file_out = []
    wr = []
    for i in range(35):
        addr_out = os.path.join(root_out, str(i+1), io_addr[1]+".ods")
        file_out.append(open(addr_out, "w"))
        wr.append(csv.writer(file_out[i], quoting = csv.QUOTE_MINIMAL))

    with open(io_addr[0], "r") as file_in:
        print io_addr[0]
        next(file_in)
        for line in file_in:
            entries = line.rstrip("\r\n").split(",")
            index = int(entries[__INDEX_DSP])-1
            entries.pop(__INDEX_DSP)
            wr[index].writerow(entries)

    for i in range(35):
        file_out[i].close()


if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr()

    for result in p.imap(crawl, list_io_addr):
        pass

    print "Completed in {} seconds".format(round(time.time()-start, 2))
    print
