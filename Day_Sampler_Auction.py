import os
import time
import numpy as np
import multiprocessing


num = 50000
start = time.time()


def get_io_addr():
    may = [(5, i) for i in range(2, 8)]
    # may = []
    june = [(6, i) for i in range(4, 26)]
    # june = []
    list_dates = may + june

    list_io_addr = []
    for date in list_dates:
        month = date[0]
        day = date[1]
        addr_in = os.path.join(str(month).rjust(2, "0"),
                               str(day).rjust(2, "0"))
        list_io_addr.append(addr_in)
    return list_io_addr


def crawl(addr_day):
    print "Processing {}".format(addr_day)

    root_in = "/mnt/rips/2016"
    list_path_in = []
    for hour in range(0, 24):
        hour_str = str(hour).rjust(2, "0")
        list_path_in.append(os.path.join(root_in, addr_day, hour_str, "part-00000"))

    total_line = 0
    for path_in in list_path_in:
        with open(path_in, "r") as file_in:
            data_list = list(file_in)
            total_line += len(data_list)


    line_indices = sorted(np.random.choice(total_line, num, replace=False))

    setoff = 0
    index = 0
    res = []
    for path_in in list_path_in:
        with open(path_in, "r") as file_in:
            data_list = list(file_in)
        while (index < num) and (line_indices[index]-setoff < len(data_list)):
            res.append(data_list[line_indices[index]-setoff])
            index += 1
        if index >= num:
            break
        setoff += len(data_list)

    root_out = "/mnt/rips2/2016"
    path_out = os.path.join(root_out, addr_day, "day_samp_raw")
    with open(path_out, "w") as file_out:
        for line in res:
            file_out.write(line)


if __name__ == '__main__':
    p = multiprocessing.Pool(4)
    list_io_addr = get_io_addr()

    for result in p.imap(crawl, list_io_addr):
        pass

    print "Completed in {} seconds\n".format(round(time.time()-start, 2))
