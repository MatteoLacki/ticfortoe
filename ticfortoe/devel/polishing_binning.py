%load_ext autoreload
%autoreload 2
import pathlib
from ticfortoe.binning import (
    get_aggregates,
    BinnedData,
    range_to_numpy_indices
)
from opentimspy.opentims import OpenTIMS
from ticfortoe.bin_borders import (
    get_intensity_bin_borders,
    get_retention_time_bin_borders,
    get_scan_bin_borders,
    get_mz_bin_borders,
    get_inv_ion_mobility_bin_borders
)
from ticfortoe.misc import (
    bin_borders_to_bin_centers,
    pivot,
    points2coefs,
    get_Bruker_TIC
)
from ticfortoe.plotting import ute_friendly_plot
import numpy as np

path = pathlib.Path('/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d')


rawdata = OpenTIMS(path)

try:
    binned_data = BinnedData.read("/tmp/test.npz")
except FileNotFoundError:
    binned_data = get_aggregates(
        rawdata=rawdata,
        statistic_name="TIC",
        frame_batch_size=100,
        verbose=True,
        intensity=get_intensity_bin_borders(),
        retention_time=get_retention_time_bin_borders(rawdata),
        inv_ion_mobility=get_inv_ion_mobility_bin_borders(rawdata),
        mz=get_mz_bin_borders(rawdata),
    )
binned_data.to_xarray()

point0 = (200, 0.65)
point1 = (501.1, 0.956)
point2 = (1200, 1.55)


binned_data.inv_ion_mobility_mz_QC_plot(
    (200, 0.65),
    (501.1, 0.956),
    (1200, 1.55)
)


inequalities_params = [
    points2coefs(point0, point1),
    points2coefs(point1, point2)
]

ufp_args = (   
    rt_min,
    Bruker_TIC,
    intensities,
    percentages
) = binned_data.get_data_for_ute_plot(rawdata, inequalities_params)

ute_friendly_plot(*ufp_args, equation=" inverse_ion_mobility <= min(0.445 + 0.001*mz, 0.53 + 0.0008*mz)")

binned_data.inv_ion_mobility_mz_QC_plot(point0, point1, point2)