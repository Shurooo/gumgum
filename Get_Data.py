import numpy as np
import Sparse_Matrix_IO as smio


# Return a numpy matrix that contain 100,000 impressions,
# with the specified ratio of positive responses and negative responses.
# The ratio is given by pos/neg
def get(addr_day, ratio):
    n = 100000
    