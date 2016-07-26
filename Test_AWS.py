import os
import json
import multiprocessing


def get_io_addr():
    may = [(5, i, j) for i in range(1, 8) for j in range(24)]
    june = [(6, i, j) for i in range(4, 26) for j in range(24)]
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

    tmax_count = 0
    imp_count = 0
    tmax_result = []
    imp_result = []
    line_count = 0
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            auction = entry["auction"]
            if auction.has_key("tmax"):
                if auction["tmax"] <= 0:
                    tmax_count += 1
                    tmax_result.append(addr_in + ": line {}".format(line_count))
            if auction.has_key("bidrequests"):
                bidreq_list = entry["auction"]["bidrequests"]
                for bidreq in bidreq_list:
                    if not (bidreq.has_key("impressions")) or (len(bidreq["impressions"]) == 0):
                        imp_count += 1
                        imp_result.append(addr_in + ": line {}".format(line_count))
            line_count += 1
    return tmax_count, tmax_result, imp_count, imp_result

if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr()

    tmax_count = 0
    imp_count = 0
    tmax_result = []
    imp_result = []
    result_list = []
    for result in p.imap(crawl, list_io_addr):
        tmax_count += result[0]
        tmax_result.extend(result[1])
        imp_count += result[2]
        imp_result.extend(result[3])


    print "{} auctions have tmax <= 0".format(tmax_count)
    print "{} bid requests do not have impressions".format(imp_count)

    with open("/home/ubuntu/Weiyi/abnormal_tmax.txt", "w") as file_out:
        file_out.write("{} auctions have tmax <= 0".format(tmax_count))
        for line in tmax_result:
            file_out.write(line + "\n")

    with open("/home/ubuntu/Weiyi/bidreq_without_imps.txt", "w") as file_out:
        file_out.write("{} bid requests do not have impressions".format(imp_count))
        for line in imp_result:
            file_out.write(line + "\n")
