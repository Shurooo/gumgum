import time
import os
import multiprocessing
import Sparse_Matrix_IO
from scipy.sparse import csr_matrix, vstack


__ADDR_ROOT = "/mnt/rips/2016"
__FEATURES = ["hour", "day", "country", "margin", "tmax", "bkc", "site_typeid", "site_cat", "browser_type",
             "bidder_id", "vertical_id", "bid_floor", "format", "product", "banner", "response"]
__FEATURES_TO_DROP = ["country"]

start = time.time()

def get_io_addr_random_sample():
    list_io_addr = []
    root = "/home/ubuntu/random_samples"
    prefix = ["all", "", "new"]
    suffix = [i for i in range(6)]
    for i in prefix:
        for j in suffix:
            file_name = i+"data"+str(j)
            addr_in = os.path.join(root, file_name+"_bin.npy")
            addr_out = os.path.join(root, file_name+"_no_country.npy")
            list_io_addr.append((addr_in, addr_out))
    return list_io_addr


def get_io_addr():
    list_day = [i for i in range(1, 8)]
    list_hour = [i for i in range(24)]
    list_month = [6]

    filename_in = "output_bin.npy"
    filename_out = "no_country.npy"

    list_io_addr = []
    for month in list_month:
        for day in list_day:
            if month == 6:
                day += 18
            for hour in list_hour:
                io_addr = os.path.join(__ADDR_ROOT,
                                       str(month).rjust(2, "0"),
                                       str(day).rjust(2, "0"),
                                       str(hour).rjust(2, "0"))
                addr_in = os.path.join(io_addr, filename_in)
                addr_out = os.path.join(io_addr, filename_out)
                list_io_addr.append((addr_in, addr_out))
    return list_io_addr


def crawl(args):
    cutoffs = args[0]
    addr_in = args[1][0]
    addr_out = args[1][1]

    new_data = []
    with open(addr_in, "r") as file_in:
        data = Sparse_Matrix_IO.load_sparse_csr(file_in)
        for line in data:
            new_line = []
            for i in range(0, len(cutoffs), 2):
                new_line.extend(line[cutoffs[i]:cutoffs[i+1]])
            new_data.append(csr_matrix(new_line))
    new_matrix = vstack(new_data)

    with (addr_out, "w") as file_out:
        Sparse_Matrix_IO.save_sparse_csr(file_out, new_matrix)


def get_feature_indices():
    get_feature_length = {
        "hour": 24,
        "day": 7,
        "country": 193,
        "margin": 5,
        "tmax": 4,
        "bkc": 1,
        "site_typeid": 3,
        "site_cat": 26,
        "browser_type": 9,
        "bidder_id": 35,
        "vertical_id": 16,
        "bid_floor": 6,
        "format": 20,
        "product": 6,
        "banner": 5,
        "response": 1
    }
    feature_indices = {}
    begin = 0
    end = 0
    for item in __FEATURES:
        length = get_feature_length[item]
        end += length
        feature_indices.update({item:(begin, end)})
        begin += length
    return feature_indices, end


def get_cutoffs():
    feature_indices, total_length = get_feature_indices()
    cutoffs = [0, total_length]
    for item in __FEATURES_TO_DROP:
        indices = feature_indices[item]
        cutoffs.append(indices[0])
        cutoffs.append(indices[1])

    return sorted(cutoffs)

if __name__ == '__main__':
    cutoffs = get_cutoffs()
    cpus = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpus)
    list_io_addr = get_io_addr()
    args = []
    for item in list_io_addr:
        args.append((cutoffs, item))

    for result in p.imap(crawl, args):
        pass

    print "Completed in {} seconds\n".format(round(time.time()-start, 2))
