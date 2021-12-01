import pathlib

from redis import Redis
from rq import Queue

from ticfortoe.defaults import get_and_save_rasterized_TICs


queue = Queue(connection=Redis(), name="ticfortoe")
path = '/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d'


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

output_folder = pathlib.Path("/mnt/ms/new/processed/.ticfortoe")
output_folder.mkdir(parents=True, exist_ok=True)


enqueued_jobs = []
for raw_folder_No, raw_folder in enumerate(iter_raw_folders(patterns)):
    target_path = output_folder/raw_folder.stem
    enqueued_job = queue.enqueue(
        get_and_save_rasterized_TICs,
        kwargs={
            "rawdata_path": str(raw_folder),
            "target_path": "/tmp/test4",
            "verbose": True
        }
    )
    enqueued_jobs.append(enqueued_job)
