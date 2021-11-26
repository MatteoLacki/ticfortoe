import collections
import numpy as np
import pandas as pd
import pathlib
import tqdm
from fast_histogram import histogram2d
from math import floor, ceil
from typing import Dict, List

from opentimspy.opentims import OpenTIMS, all_columns

from ticfortoe.intensity_counts import batch_iter



def get_x_y_tics(
    x,
    y,
    intensity,
    range_x,
    range_y,
    bins_x,
    bins_y,
    intensity_thresholds=[0, 50, 100, 150, 200]
):
    res = np.empty((len(intensity_thresholds), bins_x, bins_y))
    for thr_idx, thr in enumerate(intensity_thresholds):
        res[thr_idx] = histogram2d(
            x=x[intensity >= thr],
            y=y[intensity >= thr],
            bins=[bins_x, bins_y],
            range=[range_x, range_y],
            weights=intensity[intensity >= thr],
        )
    return res


# MAke a sister function for inverse_ion_mob
def get_TIC_conditional_on_mz_scan_intensity_bins(
    path: str,
    mz_bin_borders=None,
    scan_bin_borders=None,
    mz_step: float = 1,
    mz_left_offset: float = 0.5,
    mz_right_offset: float = 0.5,
    scan_step: int = 10,
    intensity_thresholds: List[int] = [0, 50, 100, 150, 200],
    batch_size: int = 100,
    verbose: bool = True,
):
    D = OpenTIMS(path)  # get data handle

    if mz_bin_borders is None: 
        mz_bin_borders = np.arange(
            floor(D.min_mz) - mz_left_offset,
            ceil(D.max_mz)  + mz_right_offset,
            mz_step
        )
    if scan_bin_borders is None:
        scan_bin_borders = np.arange(
            D.min_scan - 0.5,
            D.max_scan + 0.5,
            scan_step
        )
    res = np.zeros(
        (len(intensity_thresholds), len(mz_bin_borders) - 1, len(scan_bin_borders) - 1)
    )

    get_mz_scan_tics_kwargs = dict(
        bins_x=len(mz_bin_borders) - 1,
        bins_y=len(scan_bin_borders) - 1,
        range_x=[mz_bin_borders[0], mz_bin_borders[-1]],
        range_y=[scan_bin_borders[0], scan_bin_borders[-1]],
        intensity_thresholds=intensity_thresholds,
    )

    frames_bunches = batch_iter(D.ms1_frames, batch_size=batch_size)
    if verbose:
        frames_bunches = tqdm.tqdm(
            frames_bunches, total=ceil(len(D.ms1_frames) / batch_size)
        )
    for frames in frames_bunches:
        X = D.query(frames=frames, columns=["scan", "mz", "intensity"])
        res += get_x_y_tics(
            x=X["mz"],
            y=X["scan"],
            intensity=X["intensity"],
            **get_mz_scan_tics_kwargs
        )
    return res, mz_bin_borders, scan_bin_borders, intensity_thresholds


def save(stat_folder_path: str, **kwargs):
    path = pathlib.Path(stat_folder_path)
    path.mkdir(parents=True, exist_ok=True)
    for filename, obj in kwargs.items():
        np.save(file=path/filename, arr=obj)



def read(stat_folder_path: str, mmap_mode: str="r"):
    path = pathlib.Path(stat_folder_path)
    data = np.load(file=path / "data.npy", mmap_mode=mmap_mode)
    x_bin_borders = np.load(file=path / "x_bin_borders.npy", mmap_mode=mmap_mode)
    y_bin_borders = np.load(file=path / "y_bin_borders.npy", mmap_mode=mmap_mode)
    return data, x_bin_borders, y_bin_borders
