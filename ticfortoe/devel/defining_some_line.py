import matplotlib.pyplot as plt
import numpy as np

from ticfortoe.binning import (
    get_aggregates,
    BinnedData
)
from ticfortoe.misc import bin_borders_to_bin_centers, pivot, points2coefs


res_path = "/home/matteo/Projects/ticfortoe/local_results/M201203_013_Slot1-1_1_708.d"

binned_data = BinnedData.read(res_path, mmap_mode='r')


data_2D = binned_data.aggregate(
    intensity=(200, 500),
    retention_time=(
        binned_data.bin_borders["retention_time"][0]  + 1,
        binned_data.bin_borders["retention_time"][-1] - 1
    )
)

mz_centers = bin_borders_to_bin_centers(data_2D.bin_borders['mz'])
scan_centers = bin_borders_to_bin_centers(data_2D.bin_borders['scan'])

plt.imshow(
    data_2D.data,
    extent=(mz_centers[0], mz_centers[-1], scan_centers[0], scan_centers[-1])
); plt.show()

mz0, scan0 = 237, 806
mz1, scan1 = 1206, 135

intercept, slope = points2coefs(mz0, scan0, mz1, scan1)

plt.scatter(df.mz, df.scan, c=np.log1p(df.intensity))
plt.plot([mz0,mz1], [scan0, scan1], c='red', linewidth=8)
plt.xlabel("m/z")
plt.ylabel("scan")
plt.show()

plt.scatter(df.mz, df.scan, c=df.intensity)
plt.plot([mz0,mz1], [scan0, scan1], c='red', linewidth=8)
plt.xlabel("m/z")
plt.ylabel("scan")
plt.show()


