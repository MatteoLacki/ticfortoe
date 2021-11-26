%load_ext autoreload
%autoreload 2
import pathlib
import pandas as pd
import numpy as np

from ticfortoe.intensity_counts import batch_iter
from ticfortoe.mz_scan_intensity import (
    get_TIC_conditional_on_mz_scan_intensity_bins,
    save,
    read
)

path = pathlib.Path('/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d')
res, mz_bin_borders, scan_bin_borders, intensity_thresholds = get_TIC_conditional_on_mz_scan_intensity_bins(path, 
    batch_size=10, verbose=True)

save("/tmp/test", data=res, x_bin_borders=mz_bin_borders, y_bin_borders=scan_bin_borders, intensity_thresholds=intensity_thresholds)

read_res = {
    var_name: read(f"/tmp/test/{var_name}.npy")
    for var_name in (
        "data",
        "x_bin_borders",
        "y_bin_borders",
        "intensity_thresholds"
    )
}


from ticfortoe.misc import bin_borders_to_bin_centers


def get_TICs(
    data,
    x_bin_borders,
    y_bin_borders,
    intensity_thresholds,
    query
):
    TICs = {}
    for array, intensity_threshold in zip(data, intensity_thresholds):
        df = pivot(
            array,
            bin_borders_to_bin_centers(x_bin_borders),
            bin_borders_to_bin_centers(y_bin_borders)
        )
        in_region = df.eval(query).values
        TICs[intensity_threshold] = {
            "in":   df.intensity[in_region].sum(),
            "out":  df.intensity[~in_region].sum()
        }
    return TICs


get_TICs(**read_res, query="x + y < 1000")


