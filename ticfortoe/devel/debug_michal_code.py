# %load_ext autoreload
# %autoreload 2
from pathlib import Path
import os
import numpy as np
from opentimspy.opentims import OpenTIMS, all_columns

from ticfortoe.binning import iter_aggregates
from ticfortoe.bin_borders import (
    get_intensity_bin_borders,
    get_retention_time_bin_borders,
    get_scan_bin_borders,
    get_mz_bin_borders,
    get_inv_ion_mobility_bin_borders
)

if os.uname().nodename == "pinguin":
    datapath = '/home/matteo/raw_data/shortruns/M210903_008_1_1_4704.d'
else:
    datapath = '/mnt/ms/old/raw_data/majestix/ARCHIVIERT/M2109/M210903_008_1_1_4704.d'
datapath = Path(datapath)
assert datapath.exists(), f"File {datapath} does not exists."


rawdata = OpenTIMS(datapath)
first100MS1Frames = rawdata.ms1_frames[1:100] # choose whatever you want

mz_bin_borders = get_mz_bin_borders(rawdata)
scan_bin_borders = get_scan_bin_borders(rawdata)

res = next(iter_aggregates(
    rawdata=rawdata,
    frame_batches=[first100MS1Frames],
    statistic_name="TIC",
    mz=mz_bin_borders,
    scan=scan_bin_borders,
))# this is a numpy array with aggregates

# res[mz_bin_idx, scan_bin_idx]

print(f"Results of binning with:")
print(f"m/z bin borders = {mz_bin_borders}")
print(f"scan bin borders = {scan_bin_borders}")
print(res)
print(res.shape)
print("First dim correspond to m/z, the other to scans.")

np.savez_compressed("/tmp/matteos_result.npz", arr=res)