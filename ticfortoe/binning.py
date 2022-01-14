import numpy as np
import fast_histogram
import itertools
import pathlib
from typing import Dict, Iterable, List
import pandas as pd

from dataclasses import dataclass
from tqdm import tqdm
from opentimspy.opentims import OpenTIMS, all_columns

from ticfortoe.iter_ops import batch_iter, get_batch_cnt
from ticfortoe.misc import (
    bin_borders_to_bin_centers,
    get_Bruker_TIC,
    get_references_masses_and_inv_ion_mobilities,
    get_monoisotopic_mz
)
from ticfortoe.numpy_ops import dense2sparse


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
    bin_borders: dict# good things: order of insertion is guaranteed! 

    def write(self, file: str):
        np.savez_compressed(
            file=file,
            data=self.data,
            **self.bin_borders
        )

    @property
    def bin_centers(self) -> Dict[str, np.array]:
        return {
            variable_name: bin_borders_to_bin_centers(bin_borders)
            for variable_name, bin_borders in self.bin_borders.items()
        }

    def __getitem__(self, name):
        return self.bin_borders.get(name,None)

    @classmethod
    def read(cls, file: str, mmap_mode: str='r'):
        packed = np.load(file=file, mmap_mode=mmap_mode)
        data = packed['data']
        bin_borders = {}
        for a in packed:
            if a != "data":
                bin_borders[a] = packed[a] 
        return cls(data=packed["data"], bin_borders=bin_borders)

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

    def get_variables_for_mask(self, *variable_names):
        bin_centers = self.bin_centers
        return np.meshgrid(
            *(bin_centers[variable_name] for variable_name in variable_names),
            sparse=True
        )

    def get_data_for_inv_ion_mobility_mz_QC_plot(
        self
    ):
        assert all(x in self.bin_borders for x in ("inv_ion_mobility", "mz", "retention_time", "intensity")), "Missing variables for QC."
        TIC = self.data.sum(axis=(0,1))
        extent = np.hstack([
            self.bin_centers['mz'][[0,-1]],
            self.bin_centers['inv_ion_mobility'][[0,-1]]
        ])
        return TIC, extent


    def get_intensities_in_and_out_a_halfplanes_intersection(
        self,
        inequalities_params
    ):
        required_column_names = [
            "intensity",
            "retention_time",
            "inv_ion_mobility",
            "mz"
        ]
        assert set(required_column_names) == set(self.bin_borders), f"Some variables are missing from {list(self.bin_borders)}"
        mz, iim = self.get_variables_for_mask("mz", "inv_ion_mobility")
        halfplanes_intersection = np.ones((iim.shape[0], mz.shape[1]), dtype=bool)
        for a,b in inequalities_params:
            halfplanes_intersection &= iim <= a + b * mz
        rt_min = self.bin_centers["retention_time"] / 60.0
        in_intersection = self.data[:,:,halfplanes_intersection].sum(axis=2)
        outside_intersection = self.data[:,:,~halfplanes_intersection].sum(axis=2)
        return in_intersection, outside_intersection


    def get_data_for_ute_plot(
        self, 
        raw_folder_path, 
        inequalities_params
    ): 
        ZZ, Z = self.get_intensities_in_and_out_a_halfplanes_intersection(inequalities_params)
        Bruker_TIC = get_Bruker_TIC(
            raw_folder_path,
            self.bin_borders["retention_time"]
        )
        intensities = [Z.sum(axis=0),*ZZ]
        intensities.reverse()
        percentages = intensities / np.sum(intensities, axis=0)
        return rt_min, Bruker_TIC, intensities, percentages


    def get_calibrants_df(self, analysis_tdf_path):
        assert "mz" in self.bin_borders, "mz necessary"
        assert "inv_ion_mobility" in self.bin_borders, "inv_ion_mobility necessary"
        iim_calibrants = pd.DataFrame(
            {
                "formula":formula,
                "mono_mz": get_monoisotopic_mz(formula),
                "inv_ion_mobility": iim
            }
            for formula, iim in get_references_masses_and_inv_ion_mobilities(analysis_tdf_path)["inv_ion_mobility"].items()
        )
        iim_calibrants["mz_bin"] = np.searchsorted(self.bin_borders["mz"], iim_calibrants.mono_mz)
        iim_calibrants["inv_ion_mobility_bin"] = np.searchsorted(self.bin_borders["inv_ion_mobility"], iim_calibrants.inv_ion_mobility)
        return iim_calibrants

    def to_sparse(self, stat_name="TIC", get_rid_of_0=True):
        X = dense2sparse(self.data, get_rid_of_0=get_rid_of_0)
        return pd.DataFrame(
            X, 
            columns=[f"{c}_bin" for c in self.bin_borders] + [stat_name,]
        )

    def get_borders_pd(self, var_name):
        assert var_name in self.bin_borders, f"Variable {var_name} not among the binning dimensions."
        bins = self.bin_borders[var_name]
        return pd.DataFrame({
            f"{var_name}_bin": np.arange(len(bins)-1),
            f"{var_name}_start": bins[:-1],
            f"{var_name}_end": bins[1:]
        })


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
    frames: np.array=None,
    **bin_borders
) -> BinnedData:
    """A specific way of getting aggregates."""
    assert statistic_name in ("peak_count","TIC"), f"Unpermitted type of a statistic: must be either 'peak_count' of 'TIC', got {statistic_name}. Repent, pay Vatican, and return."

    if frames is None:
        frames = rawdata.ms1_frames

    frame_batches = batch_iter(
        frames,
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
