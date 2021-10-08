from ticfortoe.intensity_counts import get_intensity_distribution_df


intensity_distribution = get_intensity_distribution_df(
    "/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d",
    verbose=True,
    min_frame=10,
    max_frame=15
)

intensity_distribution = get_intensity_distribution_df(
    "/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d",
    verbose=True
)

intensity_distribution.groupby("condition_name").intensity.sum()
intensity_distribution.to_csv("test.csv")


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