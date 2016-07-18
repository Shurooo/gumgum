import time
import os
import Fields_and_Methods
import multiprocessing
import Sparse_Matrix_IO


start = time.time()


def get_io_addr_random_sample():
    list_io_addr = []
    root = "/home/ubuntu/random_samples"
    prefix = ["all", "", "new"]
    suffix = [i for i in range(6)]
    for i in prefix:
        for j in suffix:
            file_name = i+"data"+str(j)
            addr_in = os.path.join(root, file_name+"_bin.ods")
            addr_out = os.path.join(root, file_name+"_bin.npy")
            list_io_addr.append((addr_in, addr_out))
    return list_io_addr


def get_io_addr():
    list_day = [i for i in range(1, 8)]
    list_hour = [i for i in range(24)]
    list_month = [6]

    filename_in = "output_bin.ods"
    filename_out = "output_bin.npy"

    return Fields_and_Methods.make_io_addr(list_month,
                                           list_day,
                                           list_hour,
                                           filename_in,
                                           filename_out)


def crawl(io_addr):
    addr_in = io_addr[0]
    addr_out = io_addr[1]

    my_matrix = []
    with open(addr_in, "r") as data:
        print addr_in
        next(data)
        for line in data:
            line_bin = []
            entries = line.rstrip('\r\n').split(',')
            for item in entries:
                line_bin.append(int(item))
            my_matrix.append(line_bin)
    with open(addr_out, "w") as file_out:
        Sparse_Matrix_IO.save_sparse_csr(file_out, my_matrix)

    os.remove(addr_in)


if __name__ == '__main__':
    # cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(6)
    list_io_addr = get_io_addr()

    for result in p.imap(crawl, list_io_addr):
        pass

    print "Completed in {} seconds".format(round(time.time()-start, 2))
    print
