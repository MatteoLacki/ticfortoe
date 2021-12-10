import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 6)

from pathlib import Path

_input = Path("/home/matteo/Projects/ticfortoe/debug_injection_amounts/inputs")

parsed = pd.DataFrame(r for lis in map(lambda x: pd.read_csv(x).to_dict("records"), Path(_input/"parsed").glob("*.csv")) for r in lis)
parsed["rawfolder"] = pd.Series([f.split("\\")[-1] for f in parsed.folder])

folder2path = {
    Path(f).name: f 
    for f in pd.read_csv(_input/"all_raw_folders_2021_12_10__17_52.csv").folder
}
parsed["path"] = parsed.rawfolder.map(folder2path)
parsed.to_csv(_input/"all_parsed_data_for_injection_amount.csv")
