import numpy as np
import pandas as pd

from math import ceil, floor


def bin_borders_to_bin_centers(bin_borders: np.array):
    return (bin_borders[1:] + bin_borders[:-1]) / 2


def pivot(TIC2D, inv_ion_mobility_bin_centers, mz_bin_centers):
    df = pd.DataFrame(
        data=TIC2D,
        index=inv_ion_mobility_bin_centers,
        columns=mz_bin_centers
    )
    df.index.name="inv_ion_mobility"
    df.columns.name="mz"
    df = pd.melt(
        df.reset_index(),
        id_vars='inv_ion_mobility',
        value_name="intensity"
    )
    df['mz'] = df.mz.astype(float)
    df = df.query('intensity > 0')
    return df


def points2coefs(point0, point1):
    x0, y0 = point0
    x1, y1 = point1
    slope = (y1-y0)/(x1-x0)
    intercept = y0 - slope*x0
    return intercept, slope


def get_Bruker_TIC(rawdata, bins):
    bruker_intensity_min, _ = np.histogram(
        rawdata.frames["Time"][rawdata.ms1_frames-1],
        bins=bins,
        weights=rawdata.frames["SummedIntensities"][rawdata.ms1_frames-1]
    )
    return bruker_intensity_min
