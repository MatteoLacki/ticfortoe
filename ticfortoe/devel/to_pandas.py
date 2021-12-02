%load_ext autoreload
%autoreload 2
import matplotlib.pyplot as plt
import numpy as np

from ticfortoe.binning import (
    get_aggregates,
    BinnedData
)
from ticfortoe.misc import bin_borders_to_bin_centers, pivot
from ticfortoe.TIC import TICcalculation, TIC_mz_scan

# res_path = "/home/matteo/Projects/ticfortoe/ticfortoe_results/G210521_025_Slot1-29_1_1731"
res_path = "/home/matteo/Projects/ticfortoe/local_results/M201203_013_Slot1-1_1_708.d"


%%timeit
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
mz, scan = np.meshgrid(scan_centers, mz_centers, sparse=True)# this can be suplied
mask = scan <= 970.114551 - 0.6924664 * mz# and user does some expression on it

projected = BinnedData(
    data=binned_data.data[:,:,mask].sum(axis=2),
    bin_borders={k:v for k,v in binned_data.bin_borders.items() if k in ("intensity","retention_time")}
)




import matplotlib.pyplot as plt

x = np.arange(-5, 5, 0.1)
y = np.arange(-5, 5, 0.1)
xx, yy = np.meshgrid(x, y, sparse=True)



z = np.sin(xx**2 + yy**2) / (xx**2 + yy**2)
h = plt.contourf(x, y, z)
plt.axis('scaled')
plt.show()



df = pivot(data_2D.data, mz_centers, scan_centers)
df.columns = ('mz','scan','intensity')
expression_with_mz_scan = "scan <= 970.114551 - 0.6924664 * mz"
df.intensity.groupby(df.eval(expression_with_mz_scan)).sum()




plt.imshow(
    data_2D.data,
    extent=(
        mz_centers[0],
        mz_centers[-1],
        scan_centers[0],
        scan_centers[-1]
    )
)
plt.show()

DF = df.pivot(index='mz', columns='scan').fillna(0)
DF.plot()
plt.show()


TICcalculation


# getting line by eye:
# mz0, scan0 = 234, 802.2
# mz1, scan1 = 1028, 288






