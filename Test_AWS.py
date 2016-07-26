import os
import json
import multiprocessing


def get_io_addr():
    may = [(5, i, j) for i in range(1, 8) for j in range(24)]
    june = [(6, i, j) for i in range(4, 26) for j in range(24)]
    root = "/mnt/rips2/2016"

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


def crawl(addr_in, dict_country):
    print "Processing {}".format(addr_in)
    new_country = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            if entry["em"].has_key("cc"):
                country = entry["em"]["cc"]
                if not dict_country.has_key(country):
                    if new_country.has_key(country):
                        new_country[country] += 1
                    else:
                        new_country.update({country:1})

    return new_country

if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr()

    new_country = {}
    for result in p.imap(crawl, list_io_addr):
        for key in result:
            if new_country.has_key(key):
                new_country[key] += result[key]
            else:
                new_country.update({key:result[key]})

    print "{} distinct new countries recorded".format(len(new_country))
    print "{} occurences in total".format(sum(new_country.values()))

    with open("/home/ubuntu/Weiyi/new_countries.json", "w") as file_out:
        json.dump(new_country, file_out)
