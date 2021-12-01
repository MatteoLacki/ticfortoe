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
batch_size = 100
verbose = True

# raw_folder = next(iter_raw_folders(patterns))
errors = {}
raw_folder_to_intensity = {}
for raw_folder_No, raw_folder in enumerate(iter_raw_folders(patterns)):
    try:
        print(f"Analysing raw folder No {raw_folder_No}")
        print(raw_folder)
        
        res_folder = output_folder/raw_folder.stem
        res_folder.mkdir(parents=True)

        # local_raw_folder = ramdisk/raw_folder.name
        # local_raw_folder.mkdir(parents=True)
        # shutil.copy(raw_folder/"analysis.tdf", local_raw_folder)
        # shutil.copy(raw_folder/"analysis.tdf_bin", local_raw_folder)
        intensity_distribution = get_intensity_distribution_df(
            raw_folder, 
            batch_size=batch_size,
            verbose=verbose
        )
        print(intensity_distribution)

        raw_folder_to_intensity[raw_folder] = intensity_distribution
        intensity_distribution["total_intensity"] = intensity_distribution.intensity * intensity_distribution.N
        TIC_summary = intensity_distribution.groupby("condition_name").total_intensity.sum().to_frame()
        TIC_summary.to_csv(res_folder/"TIC_summary.csv")
        intensity_distribution.to_csv(res_folder/"intensity_distribution.csv")

        print("Done.\n")
    except FileExistsError:
        print(f"Folder\n{raw_folder}\nalready analysed.\n")
    except RuntimeError as exc:
        errors[raw_folder] = exc
