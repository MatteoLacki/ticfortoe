%load_ext autoreload
%autoreload 2
import pathlib
import pandas as pd
import numpy as np
import fast_histogram
import collections
import matplotlib.pyplot as plt

from math import ceil, floor
from tqdm import tqdm
from opentimspy.opentims import OpenTIMS, all_columns

from ticfortoe.iter_ops import batch_iter
from ticfortoe.misc import get_bin_borders
from typing import Iterable, List



def iter_aggregates(
    rawdata:        OpenTIMS,
    frame_batches:  Iterable[List[int]],
    operation:      str="TIC",
    **variable_specific_bin_borders
):
    columns = list(variable_specific_bin_borders)
    if operation == "TIC" and "intensity" not in columns:
        columns.append("intensity")

    _bins   = []
    _range  = []
    for var_name, bin_borders in variable_specific_bin_borders.items():
        _bins.append( len(bin_borders)-1 )
        _range.append( (0.5, len(bin_borders)-0.5) )

    for frame_batch in frame_batches:
        data = rawdata.query(frame_batch, columns=columns)
        digitized_data = [
            np.digitize(data[var_name], bin_borders)
            for var_name, bin_borders in variable_specific_bin_borders.items()
        ]
        yield fast_histogram.histogramdd(
            sample=digitized_data,
            bins=_bins,
            range=_range,
            weights = data["intensity"] if operation == "TIC" else None
        ).astype(int)# this is stupid of course, but works



def get_aggregates(
    path: str,
    operation: str="TIC",
    intensity_bin_borders: List[float]=[0,50,100,150,200,float("inf")],
    retention_time_bins_number: int=21,# dodeciles
    scan_bin_size: int=10,
    mz_bin_size: int=10,
    batch_size: int=100,
    verbose: bool=False,
):
    """A specific way of getting aggregates."""
    assert operation in ("peak_count","TIC"), f"Unpermitted type of operation: must be either 'peak_count' of 'TIC', got {operation}. Repent, pay Vatican, and return."
    rawdata = OpenTIMS(path)
    mz_bin_borders = get_bin_borders(rawdata.min_mz, rawdata.max_mz, base=mz_bin_size)
    scan_bin_borders = get_bin_borders(rawdata.min_scan, rawdata.max_scan, base=scan_bin_size)
    intensity_bin_borders = np.array(intensity_bin_borders)
    retention_time_bin_borders = np.linspace(
        start=floor(rawdata.min_retention_time),
        stop=ceil(rawdata.max_retention_time)+1,
        num=retention_time_bins_number
    )
    frame_batches = batch_iter(rawdata.ms1_frames, batch_size=batch_size)
    if verbose:
        frame_batches = tqdm(frame_batches, total=ceil(len(rawdata.ms1_frames)/batch_size))
    variable_specific_bin_borders = {
        "intensity":        intensity_bin_borders,
        "retention_time":   retention_time_bin_borders,
        "scan":             scan_bin_borders,
        "mz":               mz_bin_borders
    }
    # variable_specific_bin_borders = {
    #     # "intensity":        intensity_bin_borders,
    #     "retention_time":   retention_time_bin_borders,
    #     "scan":             scan_bin_borders,
    #     "mz":               mz_bin_borders
    # } # this is yet another possibility, for some other function.
    res = sum(
        iter_aggregates(
            rawdata,
            frame_batches,
            operation,
            **variable_specific_bin_borders
        )
    )
    return {
        "binned_data": res,
        "intensity_bin_borders": intensity_bin_borders,
        "retention_time_bin_borders": retention_time_bin_borders
        "scan_bin_borders": scan_bin_borders,
        "mz_bin_borders": mz_bin_borders,
    }


if __name__ == "__main__":
    %load_ext autoreload
    %autoreload 2
    import pathlib
    from ticfortoe.binning import get_aggregates
    path = pathlib.Path('/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d')
    res = get_aggregates(path, verbose=True)

    for name, obj in res.items():
        np.save(f"/tmp/test/{name}.npy", obj)

    binned_data = np.load('/tmp/test/binned_data.npy', mmap_mode="r")
    plt.imshow(binned_data[4,1]);plt.show()
    plt.imshow(binned_data[0,1]);plt.show()


    peak_counts = get_aggregates(path, verbose=True, operation="peak_count")
    peak_counts['binned_data']

from ticfortoe.misc import bin_borders_to_bin_centers


result_to_xarray(res)