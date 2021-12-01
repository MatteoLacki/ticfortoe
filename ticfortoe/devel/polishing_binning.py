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
    statistic_name="TIC",
    frame_batch_size=100,
    verbose=True,
    intensity=get_intensity_bin_borders(),
    retention_time=get_retention_time_bin_borders(rawdata),
    mz=get_mz_bin_borders(rawdata),
    scan=get_scan_bin_borders(rawdata)
)

binned_data.write("/tmp/test3")
binned_data.to_xarray()

binned_data.indices_in_ranges(intensity=(10,50))
binned_data.indices_in_ranges(intensity=(10,50), retention_time=(300, 500))
x = binned_data.indices_in_ranges(
    tensor_coordinates=False,
    intensity=(10,50), 
    retention_time=(300, 500)
)
binned_data.sum(intensity=(10,50), retention_time=(300, 500))
aggreg_binned_data = binned_data.aggregate(
    intensity=(10,50), 
    retention_time=(300, 500)
)
aggreg_binned_data

import matplotlib.pyplot as plt
plt.imshow(aggreg_binned_data.data)
plt.show()

binned_xa = binned_data.to_xarray()
binned_xa.where(binned_xa.intensity > 100 )
# binned_xa[binned_xa.intensity > 100]
# bb_mmapped = BinnedData.read("/tmp/test3")


# binned_data.plot(cmap="inferno")