import glob
import pathlib

from redis import Redis
from rq import Queue

from ticfortoe.jobs import get_and_save_rasterized_TICs

import os


if os.uname().nodename == "pinguin":
    connection = Redis()
else: # must be in the lab
    connection = Redis(
        host='192.168.1.176',
        port=6379, 
    )

queue = Queue(
    connection=connection,
    name="ticfortoe"
)
# queue.empty()


# path = '/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d'
# res = queue.enqueue(
#     get_and_save_rasterized_TICs,
#     kwargs={
#         "rawdata_path": path,
#         "target_path": "/tmp/test4",
#         "verbose": True
#     }
# )

patterns = []
for instr in ("gutamine", "falbala", "obelix", "majestix"):
    patterns.append(f"/mnt/ms/old/rawdata/{instr}/ARCHIVIERT/*/*.d")
    patterns.append(f"/mnt/ms/old/rawdata/{instr}/RAW/*.d")

def iter_raw_folders(patterns):
    for pattern in patterns:
        for path in glob.iglob(pattern):
            yield pathlib.Path(path)

raw_folders = list(iter_raw_folders(patterns))
_total_number_of_files = len(raw_folders)


output_folder = pathlib.Path("/mnt/ms/new/processed/.ticfortoe")
output_folder.mkdir(parents=True, exist_ok=True)


enqueued_jobs = []
# raw_folder_No, raw_folder = next(enumerate(raw_folders))
for raw_folder_No, raw_folder in enumerate(raw_folders):
    target_path = output_folder/raw_folder.stem
    print(f"Enquing raw folder No {raw_folder_No}/{_total_number_of_files}.")
    enqueued_job = queue.enqueue(
        get_and_save_rasterized_TICs,
        kwargs={
            "rawdata_path": str(raw_folder),
            "target_path": target_path,
            "verbose": True,
            "_verbose": True,
            "_total_number_of_files": _total_number_of_files,
            "_file_number": raw_folder_No 
        }
    )
    enqueued_jobs.append(enqueued_job)
