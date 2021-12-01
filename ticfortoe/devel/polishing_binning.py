%load_ext autoreload
%autoreload 2
import pathlib
from ticfortoe.binning import get_aggregates, BinnedData

path = pathlib.Path('/home/matteo/raw_data/majestix/M201203_013_Slot1-1_1_708.d')
binned_data = get_aggregates(path, verbose=True)
binned_data.write("/tmp/test3")

bb_mmapped = BinnedData.read("/tmp/test3")
