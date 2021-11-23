import numpy as np

from dataclasses import dataclass
from opentimspy.opentims import OpenTIMS
from paramidiac.c_stuff import ffi, paramidiac_lib
from typing import Protocol, List


@dataclass
class IntensityStatsMaker:
    """
    Attributes:
        path (str): Path to the raw folder.
    """
    path: str


    def __post_init__(self):
        self.raw = OpenTIMS(self.path)
        self._array_size = self.raw.max_frame + 1


    def get_frameset_by_groups(self, groups: List[int]):
        return ffi.new(
            f"int32_t[{self._array_size}]",
            [-1,*groups]
        )


    def get_one_group_frameset_by_frame_ids(self, frame_ids: List[int]):
        framesets = ffi.new(
            f"int32_t[{self._array_size}]",
            [-1] * self._array_size
        )        
        for frame_id in frame_ids:
            framesets[frame_id] = 0
        return framesets


    def get_intensity_summaries(
        self, 
        framesets, 
        intensity_threshold: int=0
    ):
        """
        Attributes:
            path (str): Path to the raw folder.
            framesets (cdata): A C table with frame assignments.
            Assuming that each group is denoted by an int and there are as many groups as max(frame_group) + 1
            threshold (int): An intensity threshold.
        """
        pointers = paramidiac_lib.work_thru(
            bytes(self.path, 'ascii'),
            framesets,
            intensity_threshold
        )
        groups_no = max(framesets) + 1
        result = []
        for group_id in range(groups_no):
            buf = ffi.buffer(pointers[group_id], 2000000*8)
            arr = np.frombuffer(buf)
            arr = arr.reshape(2000, 1000)
            result.append(arr)
        return result


    def get_MS1_intensity_summaries(
        self,
        min_time=0,
        max_time=float("inf"),
        **kwargs
    ):
        time = self.raw.frames['Time']
        isms1 = self.raw.frames['MsMsType'] == 0
        chosen_frames = (time >= min_time) & (time <= max_time) & isms1
        frame_groups = chosen_frames - 1
        return self.get_intensity_summaries(
            framesets = self.get_frameset_by_groups(frame_groups),
            **kwargs
        )[0]

