from typing import Optional

from voltpeek import constants

class Scale:
    VERTICALS = (0.1, 0.2, 0.5, 1, 2, 5, 10, 12)
    HORIZONTALS = (1e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6, 1e-3, 10e-3, 100e-3, 1)
    PROBE_DIVISIONS = (1, 10)
    MAX_VERTICAL_INDEX: int = len(VERTICALS) - 1
    MAX_HOR_INDEX: int = len(HORIZONTALS) - 1
    RANGE_FLIP_INDEX: int = 1 
    DEFAULT_VERTICAL_INDEX: int = 5 
    DEFAULT_HORIZONTAL_INDEX: int = 7

    def __init__(self) -> None:
        self._vertical_index: int = self.DEFAULT_VERTICAL_INDEX
        self._horizontal_index: int = self.DEFAULT_HORIZONTAL_INDEX
        self._high_range_flip: bool = False
        self._low_range_flip: bool = False
        self._clock_div: Optional[int] = 1
        self._fs: Optional[int] = 62500000
        self._probe_div: int = 1

    def increment_vert(self) -> None:
        if self._vertical_index < self.MAX_VERTICAL_INDEX: 
            self._vertical_index += 1     
            self._high_range_flip = self._vertical_index == self.RANGE_FLIP_INDEX + 1 
            self._low_range_flip = False 

    def decrement_vert(self) -> None:
        if self._vertical_index > 0: 
            self._vertical_index -= 1
            self._low_range_flip = self._vertical_index == self.RANGE_FLIP_INDEX
            self._high_range_flip = False

    def increment_hor(self) -> None:
        if self._horizontal_index < self.MAX_HOR_INDEX: 
            self._horizontal_index += 1

    def decrement_hor(self) -> None:
        if self._horizontal_index > 0: 
            self._horizontal_index -= 1

    @property
    def fs(self) -> Optional[int]: return self._fs

    @property
    def clock_div(self) -> Optional[int]: return self._clock_div

    @property
    def high_range_flip(self) -> bool: return self._high_range_flip

    @property
    def low_range_flip(self) -> bool: return self._low_range_flip

    @property
    def vert(self) -> float: return self.VERTICALS[self._vertical_index]
    
    @property
    def hor(self) -> float: return self.HORIZONTALS[self._horizontal_index]

    @property
    def probe_div(self) -> int: return self._probe_div

    @probe_div.setter
    def probe_div(self, probe_div: int) -> None:
        if probe_div not in self.PROBE_DIVISIONS:
            raise ValueError('Not an existing probe division.')
        self._probe_div = probe_div

    # TODO: possibly move these methods so they can be exposed to scripting API
    def get_max_sample_rate(self, memory_depth: int) -> float:
        return (memory_depth/(self.hor*constants.Display.GRID_LINE_COUNT))/2 

    def find_lowest_clock_division(self, sample_rate: float, base_clock: float) -> Optional[int]:
        for div in range(1, 65540):
            if base_clock/div <= sample_rate:
                return div
        return None

    def update_sample_rate(self, base_clock: float, memory_depth: int) -> None:
        max_sample_rate: float = self.get_max_sample_rate(memory_depth)
        self._clock_div = self.find_lowest_clock_division(max_sample_rate, base_clock)
        if self._clock_div is not None:
            self._fs = int(base_clock/self._clock_div)
