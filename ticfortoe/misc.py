import numpy as np
import pandas as pd

from math import ceil, floor


def bin_borders_to_bin_centers(bin_borders: np.array):
    return (bin_borders[1:] + bin_borders[:-1]) / 2


def pivot(array, x_bin_centers, y_bin_centers):
    df = pd.DataFrame(
        data=array,
        index=x_bin_centers,
        columns=y_bin_centers
    )
    df.index.name = "x"
    df.columns.name = "y"
    df = pd.melt(
        df.reset_index(),
        id_vars='x',
        value_name="intensity"
    )
    df['y'] = df.y.astype(float)
    df = df.query('intensity > 0')
    return df


def points2coefs(x0, y0, x1, y1):
    slope = (y1-y0)/(x1-x0)
    intercept = y0 - slope*x0
    return intercept, slope
