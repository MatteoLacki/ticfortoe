from opentimspy.opentims import OpenTIMS

from ticfortoe.binning import get_aggregates
from ticfortoe.bin_borders import (
    get_intensity_bin_borders,
    get_retention_time_bin_borders,
    get_inv_ion_mobility_bin_borders,
    get_mz_bin_borders
)



def get_and_save_rasterized_TICs(
    rawdata_path: str,
    target_path: str,
    _verbose: bool=True,
    _file_number: int=0,
    _total_number_of_files: int=0,
    **kwargs
):
    try:
        if _verbose:
            print(f"Analysing {rawdata_path}")
            if _total_number_of_files:
                print(f"File {_file_number}/{_total_number_of_files}")

        rawdata = OpenTIMS(rawdata_path)
        binned_data =  get_aggregates(
            rawdata=rawdata,
            statistic_name="TIC",
            frame_batch_size=100,
            verbose=_verbose,
            intensity=get_intensity_bin_borders(),
            retention_time=get_retention_time_bin_borders(rawdata),
            inv_ion_mobility=get_inv_ion_mobility_bin_borders(rawdata),
            mz=get_mz_bin_borders(rawdata),
            **kwargs
        )
        binned_data.write(target_path)
        return "Done"
    except Exception as exc:
        return repr(exc)