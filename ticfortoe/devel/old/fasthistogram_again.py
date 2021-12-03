%load_ext autoreload
%autoreload 2
from collections import Counter
from fast_histogram import histogram2d
from opentimspy.opentims import OpenTIMS, all_columns
import pathlib
import numpy as np
import pandas as pd

from ticfortoe.intensity_counts import conditions
from ticfortoe.mz_scan_intensity import (
    get_TIC_conditional_on_mz_scan_intensity_bins,
    save,
    read
)

path = pathlib.Path('/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d')
res, mz_bin_borders, scan_bin_borders = get_TIC_conditional_on_mz_scan_intensity_bins(path, 
    batch_size=10, verbose=True)


LIBPATH = pathlib.Path("/home/matteo/Projects/ticfortoe/ticfortoe/data/")
destination = LIBPATH/path.stem

save(destination, res, mz_bin_borders, scan_bin_borders)
res, mz_bin_borders, scan_bin_borders = read(destination) # mmap is fast!


def to_df(data, mz_bin_borders, scan_bin_borders):
    mz_bin_mids = (mz_bin_borders[1:] + mz_bin_borders[:-1]) / 2
    scan_bin_mids = (scan_bin_borders[1:] + scan_bin_borders[:-1]) / 2
    return pd.DataFrame(
        data[0],
        columns=scan_bin_mids,
        index=mz_bin_mids,
    )



def plot_wide_df(df_wide, show=True):
    import matplotlib.pyplot as plt
    plt.imshow(
        df_wide,
        aspect="auto",
        extent=[
            df_wide.index[0],
            df_wide.index[-1],
            df_wide.columns[0],
            df_wide.columns[-1]
        ]
    )
    plt.xlabel("m/z")
    plt.ylabel("scan")
    if show:
        plt.show()


df_wide = to_df(res, mz_bin_borders, scan_bin_borders)
plot_wide_df(df_wide)

half_planes = [ conditions["multiply_charged"] ]


# df_long = df.stack(dropna=True)
# df_long[df_long>0]