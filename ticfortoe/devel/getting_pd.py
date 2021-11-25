%load_ext autoreload
%autoreload 2
import pathlib
import pandas as pd

from ticfortoe.intensity_counts import batch_iter
from ticfortoe.mz_scan_intensity import (
    get_TIC_conditional_on_mz_scan_intensity_bins,
    save,
    read
)

path = pathlib.Path('/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d')
res, mz_bin_borders, scan_bin_borders = get_TIC_conditional_on_mz_scan_intensity_bins(path, 
    batch_size=10, verbose=True)

save("/tmp/test", res, mz_bin_borders, scan_bin_borders)
res, x_bin_borders, y_bin_borders = read("/tmp/test")



array = res[0]


x_y_query = 'x + y < 10'


def get_TICs(array, x_bin_borders, y_bin_borders, out_regionn_TICs):
    x_bin_centers = (x_bin_borders[1:] + x_bin_borders[:-1])/2
    y_bin_centers = (y_bin_borders[1:] + y_bin_borders[:-1])/2
    df = pd.DataFrame(array, index=x_bin_centers, columns=y_bin_centers)
    df.index.name = "x"
    df.columns.name = "y"
    df = pd.melt(
        df.reset_index(),
        id_vars='x',
        value_name="intensity"
    )
    df['y'] = df.y.astype(float)
    df = df.query('intensity > 0')
    in_region = df.eval(x_y_query).values
    in_region_TICs = df.intensity[in_region].sum()
    out_regionn_TICs = df.intensity[~in_region].sum()
    return in_region_TICs, out_regionn_TICs





