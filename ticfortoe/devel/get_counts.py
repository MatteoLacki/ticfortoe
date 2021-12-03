%load_ext autoreload
%autoreload 2
import pathlib
from ticfortoe.binning import (
    get_aggregates,
    BinnedData,
    range_to_numpy_indices
)
from ticfortoe.bin_borders import (
    get_intensity_bin_borders,
    get_retention_time_bin_borders,
    get_scan_bin_borders,
    get_mz_bin_borders
)
from opentimspy.opentims import OpenTIMS

path = pathlib.Path('/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d')
rawdata = OpenTIMS(path)

binned_data = get_aggregates(
    rawdata=rawdata,
    statistic_name="peak_count",
    frame_batch_size=100,
    verbose=True,
    intensity=get_intensity_bin_borders(),
    retention_time=get_retention_time_bin_borders(rawdata),
    mz=get_mz_bin_borders(rawdata),
    scan=get_scan_bin_borders(rawdata)
)

binned_data.write("/home/matteo/Projects/ticfortoe/local_results/M201203_013_Slot1-1_1_708_peak_count")
