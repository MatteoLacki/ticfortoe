import pandas as pd
pd.set_option('display.max_columns', None)
import pathlib

_input = pathlib.Path("/home/matteo/Projects/ticfortoe/debug_injection_amounts/inputs")

files = [
    "M210422_InjectionRamps_David.csv",
    "Ute_2021_04_09.csv",
    "Ute_2021_04_09_test.csv",
    "majestix.csv",
    "obelix.csv",
]

for _file in files:
    print(_file)
    print(pd.read_csv(_input/_file).head())
    print()

20210512_loading_amount_Gutemine.csv