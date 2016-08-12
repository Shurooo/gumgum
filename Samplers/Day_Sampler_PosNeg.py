import os
import time
import multiprocessing
import numpy as np


num = 100000
start = time.time()


def get_io_addr():
    may = [(5, i) for i in range(9, 32)]
    # may = []
    june = [(6, i) for i in range(1, 4)]
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
    root = "/mnt/rips2/2016"

    for suffix in ["pos", "neg"]:
        list_path_in = []
        for hour in range(24):
            hour_str = str(hour).rjust(2, "0")
            list_path_in.append(os.path.join(root, addr_day, hour_str, "output_" + suffix))

        total_line = 0
        for path_in in list_path_in:
            with open(path_in, "r") as file_in:
                line_count = 0
                for line in file_in:
                    line_count += 1
                total_line += line_count
        if total_line > num:
            line_indices = sorted(np.random.choice(total_line, num, replace=False))

            setoff = 0
            index = 0
            res = []
            for path_in in list_path_in:
                with open(path_in, "r") as file_in:
                    for line in file_in:
                        if line_indices[index]-setoff == 0:
                            res.append(line)
                            index += 1
                        setoff += 1
                        if index >= num:
                            break
                if index >= num:
                    break
        else:
            res = []
            for path_in in list_path_in:
                with open(path_in, "r") as file_in:
                    res.extend(list(file_in))

        path_out = os.path.join(root, addr_day, "PosNeg", "day_samp_raw_" + suffix)
        with open(path_out, "w") as file_out:
            for line in res:
                file_out.write(line)


if __name__ == '__main__':
    # cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(4)
    list_io_addr = get_io_addr()

    for result in p.imap(crawl, list_io_addr):
        pass

    print "Completed in {} seconds\n".format(round(time.time()-start, 2))
