import time
import os
import json
import operator
import multiprocessing
from functools import partial


ADDR_COUNTRY_DICT = "/home/wlu/Desktop/rips16/dicts/dict_country.json"
with open(ADDR_COUNTRY_DICT, "r") as file_in:
    __DICT_COUNTRY = json.load(file_in)

start = time.time()

ADDR_IN_ROOT = "/home/wlu/Desktop/rips16"
# ADDR_OUT_ROOT = "/home/wlu/Desktop/rips16"

month = 5
list_day = [a for a in range(1,2)]
list_hour = [b for b in range(1)]

def Crawl(hour, day):
    path_month = str(month).rjust(2, "0")
    path_day = str(day).rjust(2, "0")
    path_hour = str(hour).rjust(2, "0")
    path_in = os.path.join(ADDR_IN_ROOT, path_month, path_day, path_hour, "output.ods")

    country_sent = [0]*200
    country_res = [0]*200
    with open(path_in, "r") as file_in:
        print path_in
        for line in file_in:
            entries = line.rstrip("\r\n").split(",")
            country = int(entries[2])
            country_sent[country] += 1
            response = entries[len(entries)-1]
            if response == 1:
                country_res[country] += 1

    return [country_sent, country_res]

if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)

    country_sent = [0]*200
    country_res = [0]*200
    for day in list_day:
        partial_Crawl = partial(Crawl, day = day)
        for result in p.imap(partial_Crawl, list_hour):
            for i in range(len(country_sent)):
                if result[0][i] > 0:
                    country_sent[i] += result[0][i]
                if result[1][i] > 0:
                    country_res[i] += result[1][i]
    country_ratio = {}
    for i in range(len(country_sent)):
        if country_res[i] > 0:
            ratio = float(country_res[i]) / country_sent[i]
            country_ratio.update({i:ratio})
    sorted_country = sorted(country_ratio.iteritems(), key=operator.itemgetter(1), reverse=True)
    print sorted_country

print "Completed in {} seconds".format(round(time.time()-start, 2))
print
