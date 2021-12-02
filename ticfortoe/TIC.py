from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

import pandas as pd



@dataclass
class TICcalculation(ABC):
    data: pd.DataFrame

    def get_tic_dict(self) -> Dict[str,float]:
        """Get a dictionary of TIC per region of interest."""


@dataclass
class TIC_mz_scan(TICcalculation):
    expression_with_mz_scan: str

    def get_tic_dict(self):
        pass

    @classmethod
    def from_two_point(cls, mz0, scan0, mz1, scan1):
        det = scan0*mz1 - scan1*mz0
        assert abs(det) > 0.00000001, "Small determinant."
        A = (mz1-mz0)/det
        B = (scan0-scan1)/det
        return cls(expression_with_mz_scan=f"{A}*mz + {B}*scan <= 1")



