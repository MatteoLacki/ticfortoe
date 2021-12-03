%load_ext autoreload
%autoreload 2
import matplotlib.pyplot as plt
import numpy as np

from ticfortoe.binning import (
    get_aggregates,
    BinnedData
)
from ticfortoe.misc import pivot
from ticfortoe.TIC import TICcalculation, TIC_mz_scan
from ticfortoe.plotting import P

# res_path = "/home/matteo/Projects/ticfortoe/ticfortoe_results/G210521_025_Slot1-29_1_1731"
res_path = "/home/matteo/Projects/ticfortoe/local_results/M201203_013_Slot1-1_1_708.d"

D = BinnedData.read(res_path, mmap_mode='r')
scan, mz = D.get_variables_for_mask("scan","mz")




multiply_charged = scan >= 970.114551 - 0.6924664 * mz# and user does some expression on it
data_pp = D.data[:,:,multiply_charged].sum(axis=2)
data_p  = D.data[:,:,~multiply_charged].sum(axis=2)
data = D.data.sum(axis=(2,3))




from opentimspy.opentims import OpenTIMS
import matplotlib.pyplot as plt


rawdata = OpenTIMS('/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d')

def MS1_TIC_composition_plot(
    rawdata,
    binned_data,
    labels=["++>= 200", "++ [150,200)", "++ [100,150)", "++ [50, 100)", "++ [0,50)", "Singly Charged Ions"],
    show=True
):
    bruker_intensity_min, _ = np.histogram(
        rawdata.frames["Time"][rawdata.ms1_frames-1],
        bins=binned_data.bin_borders["retention_time"],
        weights=rawdata.frames["SummedIntensities"][rawdata.ms1_frames-1]
    )
    rt_sec = binned_data.bin_centers["retention_time"]
    rt_min = rt_sec / 60.0

    intensities = [data_p.sum(axis=0),*data_pp]
    intensities.reverse()

    plt.subplot(2, 1, 1)
    plt.scatter(
        rt_min,
        bruker_intensity_min,
        label="FULL TIC according to BRUKER"
    )
    plt.stackplot(rt_min, *intensities, labels=labels)
    plt.legend()
    plt.title("Comparison of TIC calculations. Multiply charged region defined as 'scan >= 970.114551 - 0.6924664 * mz' ")
    plt.xlabel("Retention Time [minutes]")
    plt.ylabel("% of TIC [per minute]")

    percentages = intensities / np.sum(intensities, axis=0)
    plt.subplot(2, 1, 2)
    plt.stackplot(rt_min, *percentages, labels=labels)
    plt.legend()
    plt.title("Composition of TIC in %. Multiply charged region defined as 'scan >= 970.114551 - 0.6924664 * mz' ")
    plt.xlabel("Retention Time [minutes]")
    plt.ylabel("% of TIC [per minute]")
    if show:
        plt.show()






# counts = BinnedData.read("/home/matteo/Projects/ticfortoe/local_results/M201203_013_Slot1-1_1_708_peak_count", mmap_mode='r')
# E_pp = counts.data[:,:,multiply_charged].sum(axis=2)
# E_p  = counts.data[:,:,~multiply_charged].sum(axis=2)
# E = D.data.sum(axis=(2,3))

# max_cnt = max(E_pp.max(), E_p.max())
# P(E_pp, "retention time bin", "intensity bin", "Multiply Charged", extent=extent, vmin=0, vmax=max_cnt)
# P(E_p, "retention time bin", "intensity bin", "Singly Charged", extent=extent, vmin=0, vmax=max_cnt)

# P(E_pp[4:5], "retention time bin", "intensity > 200", "Multiply Charged", vmin=0)

# plt.plot(E_pp[4:5].flatten())
# plt.show()

# plt.plot(data_pp[4:5].flatten())
# plt.show()