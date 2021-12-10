import glob
import pathlib

from ticfortoe.jobs import get_and_save_rasterized_TICs
import pandas as pd
pd.set_option('display.max_columns', None)

_input = pd.read_csv("/home/matteo/Projects/ticfortoe/ticfortoe/all_parsed_data_for_injection_amount.csv")
_total_number_of_files = len(_input)
output_folder = pathlib.Path("/mnt/ms/new/processed/.injection_amounts")
output_folder.exists()
all(pathlib.Path(raw_folder).exists() for raw_folder in _input.path)

# raw_folder_No, raw_folder = next(enumerate(_input.path))
for raw_folder_No, raw_folder in enumerate(_input.path):
    folder_name = pathlib.Path(raw_folder).stem
    target_path = output_folder/f"{folder_name}.npz"
    print(f"Calculting raw folder No {raw_folder_No + 1}/{_total_number_of_files}.")
    status = get_and_save_rasterized_TICs(
        rawdata_path=raw_folder,
        target_path=str(target_path),
        _verbose= True,
        _total_number_of_files=_total_number_of_files,
        _file_number=raw_folder_No 
    )
    print(status)
  

# from ticfortoe.binning import BinnedData
# BinnedData.read(target_path).to_xarray()


    