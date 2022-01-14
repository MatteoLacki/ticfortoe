import numpy as np
import pandas as pd
import pathlib
import sqlite3

from math import ceil, floor
import IsoSpecPy as iso


def bin_borders_to_bin_centers(bin_borders: np.array):
    return (bin_borders[1:] + bin_borders[:-1]) / 2


def pivot(TIC2D, inv_ion_mobility_bin_centers, mz_bin_centers):
    df = pd.DataFrame(
        data=TIC2D,
        index=inv_ion_mobility_bin_centers,
        columns=mz_bin_centers
    )
    df.index.name="inv_ion_mobility"
    df.columns.name="mz"
    df = pd.melt(
        df.reset_index(),
        id_vars='inv_ion_mobility',
        value_name="intensity"
    )
    df['mz'] = df.mz.astype(float)
    df = df.query('intensity > 0')
    return df


def points2coefs(point0, point1):
    x0, y0 = point0
    x1, y1 = point1
    slope = (y1-y0)/(x1-x0)
    intercept = y0 - slope*x0
    return intercept, slope


def Bruker_TIC_by_RetentionTime(raw_folder_path):
    path = pathlib.Path(raw_folder_path)/"analysis.tdf"
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        time, summedIntensities = zip(*c.execute("SELECT Time, SummedIntensities FROM Frames WHERE MsMSType=0"))
    return time, summedIntensities


def get_Bruker_TIC(raw_folder_path, bins):
    time, summedIntensities = Bruker_TIC_by_RetentionTime(raw_folder_path)
    bruker_intensity_per_minute, _ = np.histogram(
        a=time,
        bins=bins,
        weights=summedIntensities
    )
    return bruker_intensity_per_minute


def line_params_to_inequalities_expression(line_params):
    line_strings = [
        f"{p[0]} + {p[1]}*mz"
        for p in line_params
    ]
    return f"inverse_ion_mobility <= min({', '.join(line_strings)})"


def sort_along(x, ref):
    return list(np.argsort([ref.index(y) for y in x]))


def get_references_masses_and_inv_ion_mobilities(analysis_tdf_path):
    with sqlite3.connect(analysis_tdf_path) as conn:
        c = conn.cursor()
        sql = "SELECT * FROM CalibrationInfo WHERE KeyName in ('ReferenceMassPeakNames', 'MassesCorrectedCalibration', 'ReferenceMobilityPeakNames', 'MobilitiesCorrectedCalibration')"
        (
            ReferenceMassPeakNames,
            MassesCorrectedCalibration,
            ReferenceMobilityPeakNames,
            MobilitiesCorrectedCalibration
        ) = (v for _,_,v in c.execute(sql))
    MassesCorrectedCalibration = np.frombuffer(MassesCorrectedCalibration, dtype=np.float64)
    MobilitiesCorrectedCalibration = np.frombuffer(MobilitiesCorrectedCalibration, dtype=np.float64)
    ReferenceMassPeakNames = ReferenceMassPeakNames.decode('ascii').split("\x00")[:-1]
    ReferenceMobilityPeakNames = ReferenceMobilityPeakNames.decode('ascii').split("\x00")[:-1]
    return {
        "mz": dict(zip(ReferenceMassPeakNames, MassesCorrectedCalibration)),
        "inv_ion_mobility": dict(zip(ReferenceMobilityPeakNames, MobilitiesCorrectedCalibration))
    }


def get_monoisotopic_mz(formula, z: int=1):
    return (iso.Iso(formula=formula).getMonoisotopicPeakMass() + z) / z 
