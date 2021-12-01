import numpy as np
import fast_histogram
import pathlib

from dataclasses import dataclass
from tqdm import tqdm
from opentimspy.opentims import OpenTIMS, all_columns

from ticfortoe.iter_ops import batch_iter, get_batch_cnt
from typing import Iterable, List



def range_to_numpy_indices(bin_range, bin_borders):
    min_idx, max_idx = np.searchsorted(bin_borders[1:], bin_range, side="right")
    max_idx += 1
    return min_idx, max_idx


def test_range_to_numpy_indices():
    intensity_ranges = (
        (25, 80),
        (0, 200),
        (50, 1000),
        (-10, 20),
        (60, 120),
        (60, 200),
        (0, 50)
    )
    intensity_bin_borders = np.array([0, 50, 100, 150, 200, float("inf")])
    for _range in intensity_ranges:
        min_idx, max_idx = range_to_numpy_indices(_range, intensity_bin_borders)
        print(f"Range {_range} -> [{min_idx},{max_idx})")


@dataclass
class BinnedData:
    data: np.array
    bin_borders: dict

    def write(self, folder: str):
        folder = pathlib.Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        np.save(file=folder/"data.npy", arr=self.data)
        for bin_var, var_bin_borders in self.bin_borders.items():
            np.save(folder/f"{bin_var}.npy", arr=var_bin_borders)

    @classmethod
    def read(cls, folder: str, mmap_mode: str='r'):
        folder = pathlib.Path(folder)
        return cls(
            data=np.load(folder/"data.npy", mmap_mode=mmap_mode),
            bin_borders={
                name: np.load(folder/f"{name}.npy", mmap_mode=mmap_mode)
                for name in ("intensity", "retention_time", "mz", "scan")
            }
        )

    def to_xarray(self):
        import xarray
        from ticfortoe.misc import bin_borders_to_bin_centers
        return xarray.DataArray(
            data=self.data,
            dims=list(self.bin_borders),
            coords=[
                bin_borders_to_bin_centers(_bin_borders)
                for _bin_borders in self.bin_borders.values()
            ]
        )


    def indices_in_ranges(
        self, 
        tensor_coordinates=True, 
        sparse=True, 
        **bin_ranges
    ):
        index_arrays = []
        for var_name, var_bin_borders in self.bin_borders.items():
            if var_name in bin_ranges:
                min_idx, max_idx = range_to_numpy_indices(
                    bin_ranges[var_name],
                    var_bin_borders
                )
                index_arrays.append(np.arange(min_idx, max_idx))
            else:
                index_arrays.append(np.arange(len(var_bin_borders)-1))
        if tensor_coordinates:
            return np.meshgrid(*index_arrays, sparse=sparse)
        else:
            return index_arrays

    def sum(self, **bin_ranges):
        """Sum data along the provided ranges.
        """
        index_arrays = self.indices_in_ranges(**bin_ranges)
        axes = tuple([idx for idx, var_name in enumerate(self.bin_borders)
                          if var_name in bin_ranges])
        return self.data[index_arrays].sum(axis=axes)
        
    def aggregate(self, **bin_ranges):
        return self.__class__(
            data=self.sum(**bin_ranges),
            bin_borders={name: borders 
                for name, borders in self.bin_borders.items()
                if name not in bin_ranges
            }
        )

    def plot(self, show=True):
        import matplotlib.pyplot as plt
        # self.data
        # plt.imshow()
        if show:
            plt.show()




def iter_aggregates(
    rawdata:        OpenTIMS,
    frame_batches:  Iterable[List[int]],
    statistic_name: str="TIC",
    **bin_borders
):
    columns = list(bin_borders)
    if statistic_name == "TIC" and "intensity" not in columns:
        columns.append("intensity")

    _bin_borders   = []
    _range  = []
    for var_name, var_bin_borders in bin_borders.items():
        _bin_borders.append( len(var_bin_borders)-1 )
        _range.append( (0.5, len(var_bin_borders)-0.5) )

    for frame_batch in frame_batches:
        data = rawdata.query(frame_batch, columns=columns)
        digitized_data = [
            np.digitize(data[var_name], var_bin_borders)
            for var_name, var_bin_borders in bin_borders.items()
        ]
        yield fast_histogram.histogramdd(
            sample=digitized_data,
            bins=_bin_borders,
            range=_range,
            weights = data["intensity"] if statistic_name == "TIC" else None
        ).astype(np.ulonglong)



def get_aggregates(
    rawdata: OpenTIMS,
    statistic_name: str="TIC",
    frame_batch_size: int=100, 
    verbose: bool=False,
    **bin_borders
) -> BinnedData:
    """A specific way of getting aggregates."""
    assert statistic_name in ("peak_count","TIC"), f"Unpermitted type of a statistic: must be either 'peak_count' of 'TIC', got {statistic_name}. Repent, pay Vatican, and return."


    frame_batches = batch_iter(
        rawdata.ms1_frames,
        batch_size=frame_batch_size
    )

    if verbose:
        frame_batches = tqdm(
            frame_batches,
            total=get_batch_cnt(len(rawdata.ms1_frames), frame_batch_size)
        )

    return BinnedData(
        data=sum(
            iter_aggregates(
                rawdata,
                frame_batches,
                statistic_name,
                **bin_borders
            )
        ), 
        bin_borders=bin_borders
    )




if __name__ == "__main__":
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
    bb_mmapped = BinnedData.read("/tmp/test3")
