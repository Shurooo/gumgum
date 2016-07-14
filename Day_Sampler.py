import os
import random
from scipy.sparse import csr_matrix, vstack
import Sparse_Matrix_IO as smio


root = "/mnt/rips2/2016"
num = 100000

for month in [5, 6]:
    month_str = str(month).rjust(2, "0")
    for day in range(1,32):
        day_str = str(day).rjust(2, "0")
        res = []
        count = 0
        path_in_day = os.path.join(root, month_str, day_str)
        flag = 0
        for hour in range(0,24):
            try:
                hour_str = str(hour).rjust(2, "0")
                path_in = os.path.join(path_in_day, hour_str, "output_bin.npy")
                print "Processing {}".format(path_in)
                with open(path_in, "r") as file_in:
                    X = smio.load_sparse_csr(file_in)
                for line in X:
                    if count < num:
                        res.append(csr_matrix(line))
                        count += 1
                    else:
                        rand = random.randint(0, count)
                        if rand < num:
                            res[rand] = csr_matrix(line)
            except:
                flag = 1
        if flag == 0:
            path_out = os.path.join(path_in_day, "day_samp_bin.npy")
            X = vstack(res)
            with open(path_out, "w") as file_out:
                smio.save_sparse_csr(file_out, X)
