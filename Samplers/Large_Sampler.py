import os
import time
from scipy.sparse import csr_matrix, vstack
import numpy as np
import Sparse_Matrix_IO as smio


num = 100000
root = "/mnt/rips2/2016"

month = 6
day = 19

start = time.time()

line_indices = sorted(np.random.choice(24*num, 5*num, replace=False))
setoff = 0
index = 0
res = []
for hour in range(0, 24):
    path_in = os.path.join(root,
                           str(month).rjust(2, "0"),
                           str(day).rjust(2, "0"),
                           str(hour).rjust(2, "0"),
                           "output_new.npy")
    print "Processing {}".format(path_in)
    with open(path_in, "r") as file_in:
        X = smio.load_sparse_csr(file_in)
        while (index < num) and (line_indices[index]-setoff < len(X)):
            res.append(csr_matrix(X[line_indices[index]-setoff]))
            index += 1
        if index >= num:
            break
        setoff += len(X)
data = vstack(res)

path_out = os.path.join(root, "random_samples", "day_samp_large_0619.npy")
with open(path_out, "w") as file_out:
    smio.save_sparse_csr(file_out, data)

print "Completed in {} seconds\n".format(round(time.time()-start, 2))
