import numpy as np

from math import ceil, floor, log10
from opentimspy.opentims import OpenTIMS


def get_intensity_bin_borders() -> np.array:
    """Get default bin borders for intensities.
    
    Returns:
        np.array: bin borders.    
    """
    return np.array([0, 50, 100, 150, 200, float("inf")])


def get_bin_borders(_min: float, _max: float, base=10) -> np.array:
    return np.arange(
        floor(_min / base) * base,
        (ceil(_max / base) + 1) * base,
        base
    )

def get_inv_ion_mobility_bin_borders(
    rawdata: OpenTIMS,
    inv_ion_mobility_step: float=0.02
) -> np.array:
    """Get retention time bins' borders.

    Arguments:
        rawdata (OpenTIMS): The raw data connection.
        inv_ion_mobility_step: Size of each bin in 1/k0.

    Returns:
        np.array: bin borders.    
    """
    step = .02
    base = 10**ceil(-log10(step))
    return np.arange(
        floor(rawdata.min_inv_ion_mobility * base) / base,
        ceil(rawdata.max_inv_ion_mobility * base) / base + step,
        step
    )


def get_retention_time_bin_borders(
    rawdata: OpenTIMS,
    retention_time_bin_size:int=60
) -> np.array:
    """Get retention time bins' borders.

    Arguments:
        rawdata (OpenTIMS): The raw data connection.
        retention_tim_bin_size: Size of each bin in seconds.

    Returns:
        np.array: bin borders.    
    """
    return get_bin_borders(
        rawdata.min_retention_time, 
        rawdata.max_retention_time,
        base=retention_time_bin_size
    )

def get_mz_bin_borders(rawdata: OpenTIMS, mz_bin_size: int=10) -> np.array:
    """Get m/z bins' borders.

    Arguments:
        rawdata (OpenTIMS): The raw data connection.
        mz_bin_size: Size of each bin in Thompsons.

    Returns:
        np.array: bin borders.    
    """
    return get_bin_borders(
        rawdata.min_mz, 
        rawdata.max_mz,
        base=mz_bin_size
    )

def get_scan_bin_borders(rawdata: OpenTIMS, scan_bin_size: int=10) -> np.array:
    """Get scan bins' borders.

    Arguments:
        rawdata (OpenTIMS): The raw data connection.
        scan_bin_size: Size of each bin in numbers of scans.

    Returns:
        np.array: bin borders.    
    """
    return get_bin_borders(
        rawdata.min_scan,
        rawdata.max_scan,
        base=scan_bin_size
    )

