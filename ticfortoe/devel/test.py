%load_ext autoreload
%autoreload 2
from ticfortoe.intensity_counts import get_intensity_distribution_df
import pathlib

# test_path = "/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d"
path = pathlib.Path("/home/services/Projects/ticfortoe/test_data")
output_folder = pathlib.Path("/home/services/Projects/ticfortoe/test_outputs")

raw_folder_to_intensity = {}
for raw_folder in path.glob("M*.d"):
    try:
        # intensity_distribution = get_intensity_distribution_df(
        #     raw_folder,    
        #     verbose=True,
        #     min_frame=10,
        #     max_frame=15
        # )
        intensity_distribution = get_intensity_distribution_df(
            raw_folder,
            verbose=True
        )
        print(intensity_distribution)

        raw_folder_to_intensity[raw_folder] = intensity_distribution
        intensity_distribution["total_intensity"] = intensity_distribution.intensity * intensity_distribution.N
        TIC_summary = intensity_distribution.groupby("condition_name").total_intensity.sum().to_frame()
        res_folder = output_folder/raw_folder.stem
        res_folder.mkdir(exist_ok=True, parents=True)
        TIC_summary.to_csv(res_folder/"TIC_summary.csv")
        intensity_distribution.to_csv(res_folder/"intensity_distribution.csv")
    except RuntimeError:
        pass





# this will be needed to get the paths..

import requests
from typing import List


def ask_for_paths(
    patterns: List[str],
    ip: str="192.168.1.209",
    port: int=8958
):
    return requests.post(f"http://{ip}:{str(port)}/find", json={"query":patterns}).json()


all_paths = ask_for_paths("*")
len(all_paths)

ask_for_paths("M201203")
ask_for_paths("G210115*.d")
ask_for_paths(["G210115_009_Slot1-1_1_689.d"])
ask_for_paths("G210115_009_Slot1-1_1_689.d")
ask_for_paths()