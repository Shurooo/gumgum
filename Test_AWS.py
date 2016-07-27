import os
import csv
import json
import operator
import multiprocessing


def get_io_addr():
    may = [(5, i, j) for i in range(1, 8) for j in range(24)]
    # may = []
    # june = [(6, i, j) for i in range(4, 26) for j in range(24)]
    june = []
    root = "/mnt/rips/2016"

    list_io_addr = []
    for item in may+june:
        month = item[0]
        day = item[1]
        hour = item[2]
        io_addr = os.path.join(root,
                               str(month).rjust(2, "0"),
                               str(day).rjust(2, "0"),
                               str(hour).rjust(2, "0"),
                               "part-00000")
        addr_in = os.path.join(io_addr)
        list_io_addr.append(addr_in)
    return list_io_addr


def crawl(addr_in):
    print "Processing {}".format(addr_in)

    dict_domain = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            domain = (entry["auction"]["site"]["domain"])
            if (domain == None) or (len(domain) == 0):
                domain = "NONE"
            if dict_domain.has_key(domain):
                dict_domain[domain] += 1
            else:
                dict_domain.update({domain:1})

    return dict_domain

if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr()

    dict_domain = {}
    for result in p.imap(crawl, list_io_addr):
        for key in result:
            if dict_domain.has_key(key):
                dict_domain[key] += result[key]
            else:
                dict_domain.update({key:result[key]})

    print "{} unique domains recorded".format(len(dict_domain))

    sorted_domain = sorted(dict_domain.items(), key=operator.itemgetter(1), reverse=True)
    with open("/home/ubuntu/Weiyi/domains.ods", "w") as file_out:
        wr = csv.writer(file_out)
        for item in sorted_domain:
            wr.writerow(item)
