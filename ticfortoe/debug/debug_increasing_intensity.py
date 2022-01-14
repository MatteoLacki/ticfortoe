from opentimspy.opentims import OpenTIMS

from ticfortoe.binning import get_aggregates
from ticfortoe.bin_borders import (
    get_intensity_bin_borders,
    get_retention_time_bin_borders,
    get_inv_ion_mobility_bin_borders,
    get_mz_bin_borders
)

rawdata_path = '/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d'
target_path = "/tmp/test13.npz"
_verbose = True

rawdata = OpenTIMS(rawdata_path)
binned_data =  get_aggregates(
    rawdata=rawdata,
    statistic_name="TIC",
    frame_batch_size=100,
    verbose=_verbose,
    intensity=get_intensity_bin_borders(),
    retention_time=get_retention_time_bin_borders(rawdata),
    inv_ion_mobility=get_inv_ion_mobility_bin_borders(rawdata),
    mz=get_mz_bin_borders(rawdata)
)

binned_data.data[:,1,10,10]
# binned_data.write(target_path)