import numpy as np
import fast_histogram
import pathlib

from dataclasses import dataclass
from math import ceil, floor
from tqdm import tqdm
from opentimspy.opentims import OpenTIMS

from ticfortoe.iter_ops import batch_iter
from ticfortoe.misc import get_bin_borders
from typing import Iterable, List



@dataclass
class BinnedData:
    data: np.array
    bins: dict

    def write(self, folder: str):
        folder = pathlib.Path(folder)
        folder.mkdir(parents=True, exist_ok=False)
        np.save(file=folder/"data.npy", arr=self.data)
        for bin_var, bin_borders in self.bins.items():
            np.save(folder/f"{bin_var}.npy", arr=bin_borders)

    @classmethod
    def read(cls, folder: str, mmap_mode: str='r'):
        folder = pathlib.Path(folder)
        return cls(
            data=np.load(folder/"data.npy", mmap_mode=mmap_mode),
            bins={
                name: np.load(folder/f"{name}.npy", mmap_mode=mmap_mode)
                for name in ("intensity", "retention_time", "mz", "scan")
            }
        )

    def to_xarray(self):
        import xarray
        from ticfortoe.misc import bin_borders_to_bin_centers
        return xarray.DataArray(
            data=self.data,
            dims=list(self.bins),
            coords=[
                bin_borders_to_bin_centers(_bins)
                for _bins in self.bins.values()
            ]
        )



def iter_aggregates(
    rawdata:        OpenTIMS,
    frame_batches:  Iterable[List[int]],
    operation:      str="TIC",
    **variable_specific_bin_borders
):
    columns = list(variable_specific_bin_borders)
    if operation == "TIC" and "intensity" not in columns:
        columns.append("intensity")

    _bins   = []
    _range  = []
    for var_name, bin_borders in variable_specific_bin_borders.items():
        _bins.append( len(bin_borders)-1 )
        _range.append( (0.5, len(bin_borders)-0.5) )

    for frame_batch in frame_batches:
        data = rawdata.query(frame_batch, columns=columns)
        digitized_data = [
            np.digitize(data[var_name], bin_borders)
            for var_name, bin_borders in variable_specific_bin_borders.items()
        ]
        yield fast_histogram.histogramdd(
            sample=digitized_data,
            bins=_bins,
            range=_range,
            weights = data["intensity"] if operation == "TIC" else None
        ).astype(np.ulonglong)



def get_aggregates(
    path: str,
    tic_or_count: str="TIC",
    intensity_bin_borders: List[float]=[0,50,100,150,200,float("inf")],
    retention_time_bins_number: int=21,# dodeciles
    scan_bin_size: int=10,
    mz_bin_size: int=10,
    batch_size: int=100,
    verbose: bool=False,
) -> BinnedData:
    """A specific way of getting aggregates."""
    assert tic_or_count in ("peak_count","TIC"), f"Unpermitted type of operation: must be either 'peak_count' of 'TIC', got {tic_or_count}. Repent, pay Vatican, and return."

    rawdata = OpenTIMS(path)

    frame_batches = batch_iter(rawdata.ms1_frames, batch_size=batch_size)
    if verbose:
        frame_batches = tqdm(frame_batches, total=ceil(len(rawdata.ms1_frames)/batch_size))

    bins = dict(
        intensity = np.array(intensity_bin_borders),
        retention_time = np.linspace(
            start=floor(rawdata.min_retention_time),
            stop=ceil(rawdata.max_retention_time)+1,
            num=retention_time_bins_number
        ),
        mz = get_bin_borders(
            rawdata.min_mz, 
            rawdata.max_mz,
            base=mz_bin_size
        ),
        scan = get_bin_borders(
            rawdata.min_scan,
            rawdata.max_scan,
            base=scan_bin_size
        ),
    )
    result = sum(
        iter_aggregates(
            rawdata,
            frame_batches,
            tic_or_count,
            **bins
        )
    )
    return BinnedData(data=result, bins=bins)






if __name__ == "__main__":
    import pathlib
    from ticfortoe.binning import get_aggregates
    path = pathlib.Path('/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d')
    path = pathlib.Path('/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d')
    binned_data = get_aggregates(path, verbose=True)
    binned_data.write("/tmp/test3")

    bb_mmapped = BinnedData.read("/tmp/test3")

    import matplotlib.pyplot as plt
    plt.imshow(binned_data.data[4,1]);plt.show()
    plt.imshow(binned_data.data[0,1]);plt.show()
    # would be nice to add plots to the class.
