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


def get_bin_borders(_min, _max, base=10):
    return np.arange(
        floor(_min / base) * base,
        (ceil(_max / base) + 1) * base,
        base
    )



