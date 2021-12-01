from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class BinBorders(ABC):
    variable_name: str

    @property
    @abstractmethod
    def bin_borders(self):
        """Get bin borders."""

    @property
    def bin_number(self):
        """Get the number of bins."""
        return len(self.bin_borders)-1
    
    @property
    def range(self):
        """Get the range of bins."""
        return self.bin_borders[0], self.bin_borders[-1]


@dataclass
class BinBordersByBinNumber(BinBorders):
    bin_number: int

    @property
    def bin_borders(self):

