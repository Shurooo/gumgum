import os
import json
import multiprocessing


def get_io_addr():
    may = [(5, i, j) for i in range(4, 26) for j in range(24)]
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

    count = 0
    line_count = 0
    result_list = []
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            if not (entry["auction"].has_key("bidrequests")) or (len(entry["auction"]["bidrequests"]) == 0):
                count += 1
                result_list.append(addr_in + ": line {}".format(line_count))
            line_count += 1
    return count, result_list

if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr()

    count = 0
    result_list = []
    for result in p.imap(crawl, list_io_addr):
        count += result[0]
        result_list.extend(result[1])


    print "{} auctions do not have bid requests".format(count)

    with open("/home/ubuntu/Weiyi/auctions_without_bidreqts_may.txt", "w") as file_out:
        file_out.write("{} auctions do not have bid requests\n".format(count))
        for line in result_list:
            file_out.write(line + "\n")
