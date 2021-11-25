%load_ext autoreload
%autoreload 2
from ticfortoe.mz_scan_intensity import (
    get_TIC_conditional_on_mz_scan_intensity_bins,
    save,
    read
)
from ticfortoe.intensity_stats import IntensityStatsMaker
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import fast_histogram

path = '/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d'

ism = IntensityStatsMaker(path)

ms1frame = ism.raw.ms1_frames[100]
mist = ism.get_intensity_summaries(ism.get_one_group_frameset_by_frame_ids([ms1frame]))[0]

frame = pd.DataFrame(ism.raw.query(ms1frame, columns=['mz','scan','intensity']))

mz_bin_borders = np.arange(1, 2002) - .5
scan_bin_borders = np.arange(1 - 0.5, 1001 + 0.5)

def borders_to_range_bincnt(borders):
    return (borders[0], borders[-1]), len(borders) - 1

range_mz, binsCnt_mz = borders_to_range_bincnt(mz_bin_borders)
range_scan, binsCnt_scan = borders_to_range_bincnt(scan_bin_borders)


fasthist = fast_histogram.histogram2d(
    x=frame.mz,
    y=frame.scan,
    weights=frame.intensity,
    bins=[binsCnt_mz, binsCnt_scan],
    range=[range_mz, range_scan]
)

numpyhist,_,_ = np.histogram2d(
    x=frame.mz,
    y=frame.scan,
    weights=frame.intensity,
    bins=[binsCnt_mz, binsCnt_scan],
    range=[range_mz, range_scan]
)

def get_diffs(a, b):
    d = a-b
    nonzero = np.sum((a>0)|(b>0))
    actually_different = d[d!=0]
    return actually_different, len(actually_different) / nonzero 

get_diffs(numpyhist, fasthist)
diffs, perc_diff = get_diffs(numpyhist, mist)

plt.hist(diffs, bins=10000)
plt.show()


mist1 = ism.get_intensity_summaries(ism.get_one_group_frameset_by_frame_ids([ms1frame]))[0]
mist2 = ism.get_intensity_summaries(ism.get_one_group_frameset_by_frame_ids([ms1frame+1]))[0]
mist3 = ism.get_intensity_summaries(ism.get_one_group_frameset_by_frame_ids([ms1frame-1]))[0]

get_diffs(mist1, mist2)
get_diffs(mist1, mist3)


fast_histogram.histogram2d(
    x=[20, 40, 50, 60, 24],
    y=[10, 30, 10, 30, 15],
    weights=[10,20,40,50,100],
    bins=[10, 4],
    range=[[0, 100], [0, 40]]
)
