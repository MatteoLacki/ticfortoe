%load_ext autoreload
%autoreload 2
from timspy.df import all_columns
from timspy.df import TimsPyDF

from ticfortoe.intensity_counts import get_intensity_distribution_df
import pathlib
import glob
import shutil

# test_path = "/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d"
# path = pathlib.Path("/home/services/Projects/ticfortoe/test_data")
path = pathlib.Path("/mnt/ms/old/rawdata/majestix")
patterns = []
for instr in ("gutamine", "falbala", "obelix", "majestix"):
    patterns.append(f"/mnt/ms/old/rawdata/{instr}/ARCHIVIERT/*/*.d")
    patterns.append(f"/mnt/ms/old/rawdata/{instr}/RAW/*.d")

def iter_raw_folders(patterns):
    for pattern in patterns:
        for path in glob.iglob(pattern):
            yield pathlib.Path(path)

output_folder = pathlib.Path("/mnt/ms/new/processed/ticfortoe")
# ramdisk = pathlib.Path("/home/matteo/Projects/ticfortoe/ramdisk")


raw_folder = next(iter_raw_folders(patterns))

res_folder = output_folder/raw_folder.stem
# local_raw_folder = ramdisk/raw_folder.name

conditions = {"singly_charged":  "inv_ion_mobility >= .0009*mz + .4744",
              "multiply_charged":"inv_ion_mobility <  .0009*mz + .4744"}

from ticfortoe.intensity_counts import parse_conditions_for_column_names

frame_numbers = None
raw_data = TimsPyDF(raw_folder)


for frame_No in tqdm.tqdm(frame_numbers) if verbose else frame_numbers:
    frame = raw_data.query(frame_No, column_names)

%%time
intensity_distribution = get_intensity_distribution_df(raw_folder, verbose=True)
# 2' 5''

%%time
intensity_distribution = get_intensity_distribution_df(
    raw_folder,
    batch_size = 100,
    verbose=True
)
# 

%%time
intensity_distribution = get_intensity_distribution_df(
    local_raw_folder,
    batch_size = 1000
)
#
