import os
import json
import multiprocessing


def get_io_addr():
    june = [(6, i, j) for i in range(4, 26) for j in range(24)]
    root = "/mnt/rips/2016"

    list_io_addr = []
    for item in june:
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


def crawl(args):
    addr_in = args[0]
    dict_country = args[1]
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

    with open("/home/ubuntu/Weiyi/dict_country.json", "r") as file_in:
        dict_country = json.load(file_in)
    args = []
    for item in list_io_addr:
        args.append((item, dict_country))

    new_country = {}
    for result in p.imap(crawl, args):
        for key in result:
            if new_country.has_key(key):
                new_country[key] += result[key]
            else:
                new_country.update({key:result[key]})

    print "{} distinct new countries recorded".format(len(new_country))
    print "{} occurences in total".format(sum(new_country.values()))

    with open("/home/ubuntu/Weiyi/new_countries.json", "w") as file_out:
        json.dump(new_country, file_out)
