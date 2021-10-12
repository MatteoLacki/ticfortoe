from ticfortoe.intensity_counts import get_intensity_distribution_df
import pathlib
import glob


# test_path = "/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d"
# path = pathlib.Path("/home/services/Projects/ticfortoe/test_data")



path = pathlib.Path("/mnt/ms/old/rawdata/majestix")
patterns = []
for instr in ("gutamine", "falbala", "obelix", "majestix"):
    patterns.append(f"/mnt/ms/old/rawdata/{instr}/ARCHIVIERT/*/*.d")
    patterns.append(f"/mnt/ms/old/rawdata/{instr}/RAW/*.d")

def iter_raw_folders(patterns):
    for pattern in patterns:
        yield from glob.iglob(pattern)

output_folder = pathlib.Path("/home/services/Projects/ticfortoe/test_outputs")
errors = {}
raw_folder_to_intensity = {}
for raw_folder in path.glob("M*.d"):
    try:
        res_folder = output_folder/raw_folder.stem
        res_folder.mkdir(parents=True)
        intensity_distribution = get_intensity_distribution_df(
            raw_folder,
            verbose=True
        )
        print(intensity_distribution)

        raw_folder_to_intensity[raw_folder] = intensity_distribution
        intensity_distribution["total_intensity"] = intensity_distribution.intensity * intensity_distribution.N
        TIC_summary = intensity_distribution.groupby("condition_name").total_intensity.sum().to_frame()
        TIC_summary.to_csv(res_folder/"TIC_summary.csv")
        intensity_distribution.to_csv(res_folder/"intensity_distribution.csv")
    except FileExistsError:
        pass
    except RuntimeError as exc:
        errors[raw_folder] = exc
