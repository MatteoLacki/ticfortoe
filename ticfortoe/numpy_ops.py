import numpy as np


def dense2sparse(X, get_rid_of_0=True, stat_name="TIC"):
    res = np.stack(np.unravel_index(np.arange(np.prod(X.shape)), X.shape) + (X.flatten(),)).T.astype(int)
    if get_rid_of_0:
        res = res[res[:,-1] != 0]
    return res
