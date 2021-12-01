%load_ext autoreload
%autoreload 2
from ticfortoe.mz_scan_intensity import (
    get_TIC_conditional_on_mz_scan_intensity_bins,
    save,
    read
)
from ticfortoe.intensity_stats import IntensityStatsMaker

import tqdm
from opentimspy.opentims import OpenTIMS
import numpy as np

path = '/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d'

ism = IntensityStatsMaker(path)


ism.get_intensity_summaries(ism.get_one_group_frameset_by_frame_ids([1,10,20]))
ism.get_MS1_intensity_summaries(intensity_threshold=100)


mist = ism.get_intensity_summaries(ism.get_one_group_frameset_by_frame_ids([1]))[0]






def get_TIC_conditional_on_mz_scan_intensity_bins_MS(
    path,
    min_time=0,
    max_time=float("inf"),
    intensity_thresholds = [0, 50, 100, 150, 200],
    verbose = True,
    **kwargs
):
    D = OpenTIMS(path)

    assert D.min_mz >= 0, "Minimal m/z smaller than Startrek presumed."
    assert D.max_mz <= 2000, "Maximal m/z smaller than Startrek presumed."
    assert D.min_scan >= 0, "Minimal scan smaller than Startrek presumed."
    assert D.max_scan <= 1000, "Maximal scan smaller than Startrek presumed."

    mz_bin_borders = np.arange(1, 2002) - .5
    scan_bin_borders = np.arange(1 - 0.5, 1001 + 0.5)
    res = np.zeros((len(intensity_thresholds), 2000, 1000))

    enum = enumerate(intensity_thresholds)
    if verbose:
        enum = tqdm.tqdm(enum)
    for i, intensity_threshold in enum:
        res[i] = get_MS1_intensity_summaries(path, intensity_threshold)
    return res, mz_bin_borders, scan_bin_borders

res_Startek, mz_bin_borders, scan_bin_borders = get_TIC_conditional_on_mz_scan_intensity_bins_MS(path)
# this script needs more attention!

res, mz_bin_borders2, scan_bin_borders2 = get_TIC_conditional_on_mz_scan_intensity_bins(
    path,
    mz_bin_borders=mz_bin_borders,
    scan_bin_borders=scan_bin_borders,
    batch_size=10,
    verbose=True,
    scan_step=1,
    mz_step=1
)

res.shape
res_Startek.shape

import matplotlib.pyplot as plt

diff = (res - res_Startek)
len(diff[(res > 0) | (res_Startek > 0)].flatten())

plt.hist(diff[diff != 0].flatten(), bins=101)
plt.show()



# 
intensities_ab_thr = sum_ops.get_ms1_intensity_summaries(path, 0)
res, _, _ = get_TIC_conditional_on_mz_scan_intensity_bins(
    path,
    mz_bin_borders=mz_bin_borders,
    scan_bin_borders=scan_bin_borders,
    batch_size=10,
    verbose=True,
    scan_step=1,
    mz_step=1,
    intensity_thresholds=[0]
)
res = res[0]
res.shape
intensities_ab_thr
intensities_ab_thr.shape
diffs = intensities_ab_thr - res


plt.hist(diffs[diffs != 0].flatten(), bins=101)
plt.show()


from fast_histogram import histogram2d

D = OpenTIMS(path)
all_data = D.query(D.ms1_frames)