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

path = pathlib.Path('/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d')
rawdata = OpenTIMS(path)



# need to have few methods for generating borders of dimensions

intensity_bin_borders = [0,50,100,150,200,float("inf")]
mz_bin_borders = get_bin_borders(rawdata.min_mz, rawdata.max_mz, base=10)
scan_bin_borders = get_bin_borders(rawdata.min_scan, rawdata.max_scan, base=10)
intensity_bin_borders = np.array(intensity_bin_borders)
retention_time_bin_borders = np.linspace(
    start=floor(rawdata.min_retention_time),
    stop=ceil(rawdata.max_retention_time)+1,
    num=21# dodeciles
)
batch_size = 100
frame_batches = batch_iter(rawdata.ms1_frames, batch_size=batch_size)
verbose = True
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
# }
operation = "TIC"


def iter_aggregates(
    rawdata:        OpenTIMS,
    frame_batches:  Iterable[List[int]],
    operation:      str="TIC",
    **variable_specific_bin_borders
):
    assert operation in ("peak_count","TIC"), f"Unpermitted type of operation: must be either 'peak_count' of 'TIC', got {operation}. Repent, pay Vatican, and return."
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
        )

res = sum(iter_aggregates(rawdata, frame_batches, "TIC", **variable_specific_bin_borders))




res.shape
np.save('/tmp/test/res.npy', res)
np.load('/tmp/test/res.npy', mmap_mode="r")


plt.imshow(res[0]);plt.show()
plt.imshow(res[4,1]);plt.show()
np.all(res[4,10] == 0)


# a bit slowish
# TICs = collections.Counter()
# for mz_bin_scan, intensity in zip(zip(mz_bins, scans), intensities):
#     TICs[mz_bin_scan] += intensity
