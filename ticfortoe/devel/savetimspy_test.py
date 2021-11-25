from savetimspy import SaveTIMS
from opentimspy import OpenTIMS

D = OpenTIMS('/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d')

s = SaveTIMS(D, '/tmp/testsavetimspy3.d')
s.save_frame(
    mzs=[601.3, 600.5],
    scans=[34, 35],
    intensities=[100, 500],
    total_scans=100
)
s.close()


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


path = '/tmp/testsavetimspy3.d'
ism = IntensityStatsMaker(path)
mist = ism.get_intensity_summaries(ism.get_one_group_frameset_by_frame_ids([1]))[0]


frame = pd.DataFrame(
    ism.raw.query(1, columns=['mz','scan','intensity'])
)

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
