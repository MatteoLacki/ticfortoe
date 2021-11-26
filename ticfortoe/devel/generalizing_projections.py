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


path = pathlib.Path('/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d')
D = OpenTIMS(path)


frame_batches = batch_iter(D.ms1_frames, batch_size=100)






# need to have few methods for generating borders of dimensions

intensity_bin_borders = [0,50,100,150,200,float("inf")]
mz_bin_borders = get_bin_borders(D.min_mz, D.max_mz, base=10)
scan_bin_borders = get_bin_borders(D.min_scan, D.max_scan, base=10)
intensity_bin_borders = np.array(intensity_bin_borders)
retention_time_bin_borders = np.linspace(
    start=floor(D.min_retention_time),
    stop=ceil(D.max_retention_time)+1,
    num=21# dodeciles
)

def 

# frame_batch = next(batch_iter(D.ms1_frames, batch_size=100))
for frame_batch in frame_batches:
    data = D.query(
        frame_batch,
        columns=columns
    )


# change scans into proper borders! That will massively simplify the code!
mzs = frames["mz"]
scans = frames["scan"]
intensities = frames["intensity"]
retention_times = frames["retention_time"]

mz_bins = np.digitize(mzs, mz_bin_borders)
intensity_bins = np.digitize(intensities, intensity_bin_borders)
retention_time_bins = np.digitize(retention_times, retention_time_bin_borders)
# this could be extracted one after another


res = fast_histogram.histogramdd(
    sample=(
        intensity_bins,
        retention_time_bins,
        frames['scan'],
        mz_bins,
    ),
    bins=(
        len(intensity_bin_borders)-1,
        len(retention_time_bin_borders)-1,
        len(scan_bin_borders)-1,
        len(mz_bin_borders)-1,
    ),
    range=(
        (0.5, len(intensity_bin_borders)-.5),
        (0.5, len(retention_time_bin_borders)-.5),
        (scan_bin_borders[0], scan_bin_borders[-1]),
        (0.5 , len(mz_bin_borders)-.5),
    ),
    weights = frames["intensity"]
)

res.shape
np.save('/tmp/test/res.npy', res)
np.load('/tmp/test/res.npy', mmap_mode="r")



plt.imshow(res[4,1]);plt.show()
np.all(res[4,10] == 0)


# a bit slowish
# TICs = collections.Counter()
# for mz_bin_scan, intensity in zip(zip(mz_bins, scans), intensities):
#     TICs[mz_bin_scan] += intensity
