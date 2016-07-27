import os
import multiprocessing
import Process_Margin as process


def get_io_addr(dates):
    root = "/mnt/rips/2016"
    list_io_addr = []
    for item in dates:
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
    return process.run(addr_in)


if __name__ == '__main__':
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr(process.get_dates())

    for result in p.imap(crawl, list_io_addr):
        process.add_result(result)

    process.get_result()
