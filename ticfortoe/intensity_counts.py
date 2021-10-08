import collections
import pandas as pd
from itertools import islice
import tqdm

from timspy.df import all_columns
from timspy.df import TimsPyDF
from typing import Dict, Iterable



conditions = {"singly_charged":  "inv_ion_mobility >= .0009*mz + .4744",
              "multiply_charged":"inv_ion_mobility <  .0009*mz + .4744"}


def parse_conditions_for_column_names(conditions):
    used_columns = set({})
    for condition in conditions.values():
        for column_name in all_columns:
            if column_name in condition:
                used_columns.add(column_name)
    return list(used_columns)


def sum_conditioned_counters(conditioned_counters, conditions):
    """Sum counters in dictionaries.
        
    Simply aggregates different counters.

    Args:
        conditioned_counters (iterable): Iterable of dictionaries with keys corresponding to condition names and values being Counters.
        conditions (iterable): names of all conditions.
    Returns:
        dict: A dictionary with keys corresponding to condition names and values being collections.Counter.
    """
    res = {name: collections.Counter() for name in conditions}
    for dct in conditioned_counters:
        for name in dct:
            res[name] += dct[name]
    return res


def sum_counters(counters):
    """Sum counters."""
    res = collections.Counter()
    for cnt in counters:
        res += cnt
    return res


def counter2df(counter, values_name="intensity"):
    """Represent a counter as a data frame. 

    Args:
        counter (dict): A mapping between values and counts.
        values_name (str): Name for the column representing values.

    Return:
        pd.DataFrame: A data frame with values and counts, sorted by values.
    """
    return pd.DataFrame(dict(zip((values_name,"N"), zip(*counter.items())))).sort_values(values_name)


def iter_conditional_intensity_counts(
    raw_data: TimsPyDF,
    conditions: Dict[str,str] = conditions,
    frame_numbers: list=None,
    verbose: bool=False
) -> Iterable[Dict[str, collections.Counter]]:
    column_names = parse_conditions_for_column_names(conditions)
    column_names.append("intensity")
    if frame_numbers is None:
        frame_numbers = raw_data.ms1_frames
    for frame_No in tqdm.tqdm(frame_numbers) if verbose else frame_numbers:
        frame = raw_data.query(frame_No, column_names)
        yield {condition_name: collections.Counter(frame.query(condition).intensity) 
               for condition_name, condition in conditions.items()}



def intensity_counts_to_df(intensity_count):
    empty_result = all(len(cnt) == 0 for cnt in intensity_count.values())
    if empty_result:
        return pd.DataFrame()
    else:
        dfs_list = []
        for condition_name in intensity_count:
            df = counter2df(intensity_count[condition_name])
            df["condition_name"] = condition_name
            dfs_list.append(df)
        return pd.concat(dfs_list, ignore_index=True)



def get_intensity_distribution_df(
    path_to_data: str,
    conditions: Dict[str,str] = conditions,
    frame_numbers: list=None,
    verbose: bool = False,
    min_frame: int = None,
    max_frame: int = None,
):
    raw_data = TimsPyDF(path_to_data)
    conditional_intensity_counts = iter_conditional_intensity_counts(
        raw_data,
        conditions,
        verbose=True
    )
    conditional_intensity_counts = islice(conditional_intensity_counts, min_frame, max_frame)
    intensity_counts = sum_conditioned_counters(conditional_intensity_counts, conditions)
    return intensity_counts_to_df(intensity_counts)
