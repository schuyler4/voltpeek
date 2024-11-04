from enum import Enum
from typing import TypedDict

from voltpeek import constants
from voltpeek.helpers import engineering_units, two_sig_figs

class Selected_Cursor(Enum):
    HOR1 = 0
    HOR2 = 1
    VERT1 = 2
    VERT2 = 3

class Cursor_Data(TypedDict):
    h1: str
    h2: str
    hdelta: str
    v1: str
    v2: str
    vdelta: str

class Cursors:
    CURSOR_COUNT = 4
    MAX_DIGITS = 4

    def __init__(self) -> None:
        self._hor1_pos: int = 10  
        self._hor2_pos: int = 20
        self._vert1_pos: int = 10
        self._vert2_pos: int = 20
        self._hor_visible: bool = False
        self._vert_visible: bool = False
        self._selected_cursor: Selected_Cursor = Selected_Cursor.HOR1

    @property
    def hor1_pos(self) -> int: return self._hor1_pos

    @property
    def hor2_pos(self) -> int: return self._hor2_pos

    @property
    def vert1_pos(self) -> int: return self._vert1_pos

    @property
    def vert2_pos(self) -> int: return self._vert2_pos

    @property
    def hor_visible(self) -> bool: return self._hor_visible

    @property
    def vert_visible(self) -> bool: return self._vert_visible

    @property
    def selected_cursor(self) -> bool: return self._selected_cursor

    def _increment_hor1(self) -> None: 
        if self._hor1_pos < constants.Display.SIZE-1: 
            self._hor1_pos += 1 
    
    def _decrement_hor1(self) -> None: 
        if self._hor1_pos > 1: 
            self._hor1_pos -= 1

    def _increment_hor2(self) -> None: 
        if self._hor2_pos < constants.Display.SIZE-1: 
            self._hor2_pos += 1

    def _decrement_hor2(self) -> None: 
        if self._hor2_pos > 1: 
            self._hor2_pos -= 1

    def _increment_vert1(self) -> None: 
        if self._vert1_pos < constants.Display.SIZE-1: 
            self._vert1_pos += 1

    def _decrement_vert1(self) -> None:
        if self._vert1_pos > 1: 
            self._vert1_pos -= 1

    def _increment_vert2(self) -> None:
        if self._vert1_pos < constants.Display.SIZE-1: 
            self._vert2_pos += 1

    def _decrement_vert2(self) -> None: 
        if self._vert2_pos > 1: 
            self._vert2_pos -= 1

    def increment_hor(self) -> None:
        if self._selected_cursor == Selected_Cursor.HOR1:
            self._increment_hor1()
        elif self._selected_cursor == Selected_Cursor.HOR2:
            self._increment_hor2()

    def decrement_hor(self) -> None:
        if self._selected_cursor == Selected_Cursor.HOR1:
            self._decrement_hor1()
        elif self._selected_cursor == Selected_Cursor.HOR2:
            self._decrement_hor2()

    def increment_vert(self) -> None:
        if self._selected_cursor == Selected_Cursor.VERT1:
            self._increment_vert1()
        elif self._selected_cursor == Selected_Cursor.VERT2:
            self._increment_vert2()

    def decrement_vert(self) -> None:
        if self._selected_cursor == Selected_Cursor.VERT1:
            self._decrement_vert1()
        elif self._selected_cursor == Selected_Cursor.VERT2:
            self._decrement_vert2()

    def toggle_hor(self) -> None: 
        self._hor_visible = not self._hor_visible
        if self._hor_visible:
            self._selected_cursor = Selected_Cursor.HOR1 

    def toggle_vert(self) -> None: 
        self._vert_visible = not self._vert_visible
        if self._vert_visible:
            self._selected_cursor = Selected_Cursor.VERT1 

    def toggle(self) -> None:
        self._hor_visible = not self._hor_visible
        self._vert_visible = not self._vert_visible
        self._selected_cursor = Selected_Cursor.HOR1

    def next_cursor(self) -> None: 
        if not self.hor_visible and self._selected_cursor.value <= 1:
            self._selected_cursor = Selected_Cursor.VERT1
        elif not self.vert_visible and self._selected_cursor.value >= 2:
            self._selected_cursor = Selected_Cursor.HOR1
        elif self._selected_cursor.value < self.CURSOR_COUNT - 1 and self._hor_visible and self._vert_visible: 
            self._selected_cursor = Selected_Cursor(self._selected_cursor.value + 1)        
        elif self._hor_visible and self._selected_cursor.value < 1:
            self._selected_cursor = Selected_Cursor(self._selected_cursor.value + 1)        
        elif self._vert_visible and self._selected_cursor.value < self.CURSOR_COUNT - 1:
            self._selected_cursor = Selected_Cursor(self._selected_cursor.value + 1)        
        elif self._hor_visible:
            self._selected_cursor = Selected_Cursor.HOR1
        elif self._vert_visible:
            self._selected_cursor = Selected_Cursor.VERT1

    def _get_hor_voltage(self, vertical_setting: float, cursor_height: int) -> float:
        pixel_amplitude: float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        pixel_resolution: float = vertical_setting/pixel_amplitude
        corrected_height: int = constants.Display.SIZE - cursor_height
        voltage: float = float((corrected_height-(constants.Display.SIZE/2))*pixel_resolution)
        return voltage 

    def _get_vert_time(self, horizontal_setting: float, cursor_offset: int) -> float:
        pixel_offset: float = float(constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        pixel_resolution: float = horizontal_setting/pixel_offset
        time: float = float((cursor_offset*pixel_resolution) - horizontal_setting*(constants.Display.GRID_LINE_COUNT/2)) 
        return time 

    def get_hor1_voltage(self, vertical_setting: float) -> float: 
        return round(self._get_hor_voltage(vertical_setting, self._hor1_pos), self.MAX_DIGITS)
    
    def _get_hor1_voltage_unrounded(self, vertical_setting: float) -> float: 
        return self._get_hor_voltage(vertical_setting, self._hor1_pos)
    
    def _get_hor2_voltage_unrounded(self, vertical_setting: float) -> float: 
        return self._get_hor_voltage(vertical_setting, self._hor2_pos)

    def get_hor2_voltage(self, vertical_setting: float) -> float: 
        return round(self._get_hor_voltage(vertical_setting, self._hor2_pos), self.MAX_DIGITS)

    def get_delta_voltage(self, vertical_setting: float) -> float:
        unrounded_result: float = self._get_hor1_voltage_unrounded(vertical_setting) - self._get_hor2_voltage_unrounded(vertical_setting)
        return round(unrounded_result, self.MAX_DIGITS)

    def _get_vert1_time_unrounded(self, horizontal_setting: float) -> float: 
        return self._get_vert_time(horizontal_setting, self._vert1_pos)

    def _get_vert2_time_unrounded(self, horizontal_setting: float) -> float: 
        return self._get_vert_time(horizontal_setting, self._vert2_pos)

    def get_vert1_time(self, horizontal_setting: float) -> float: 
        return round(self._get_vert_time(horizontal_setting, self._vert1_pos), self.MAX_DIGITS)

    def get_vert2_time(self, horizontal_setting: float) -> float: 
        return round(self._get_vert_time(horizontal_setting, self._vert2_pos), self.MAX_DIGITS)

    def _get_delta_time_unrounded(self, horizontal_setting: float) -> float:
        return self._get_vert1_time_unrounded(horizontal_setting) - self._get_vert2_time_unrounded(horizontal_setting)

    def get_delta_time(self, horizontal_setting: float) -> float: 
        return round(self._get_delta_time_unrounded(horizontal_setting), self.MAX_DIGITS)

    def get_delta_frequency(self, horizontal_setting: float) -> float: 
        if self._get_delta_time_unrounded(horizontal_setting) != 0:
            return abs(round(1/self._get_delta_time_unrounded(horizontal_setting), self.MAX_DIGITS))
        else:
            return float('NaN')

    def get_cursor_dict(self, hor_setting:bool, vert_setting:bool) -> Cursor_Data:
        h1: str = engineering_units(two_sig_figs(self.get_hor1_voltage(vert_setting))) + 'V' if self.hor_visible else ''
        h2: str = engineering_units(two_sig_figs(self.get_hor2_voltage(vert_setting))) + 'V' if self.hor_visible else '' 
        hdelta: str = engineering_units(two_sig_figs(self.get_delta_voltage(vert_setting))) + 'V' if self.hor_visible else ''
        print(two_sig_figs(self.get_vert1_time(hor_setting)))
        v1: str = engineering_units(two_sig_figs(self.get_vert1_time(hor_setting))) + 's' if self.vert_visible else ''
        v2: str = engineering_units(two_sig_figs(self.get_vert2_time(hor_setting))) + 's' if self.vert_visible else ''
        vdelta: str = engineering_units(two_sig_figs(self.get_delta_time(hor_setting))) + 's' if self.vert_visible else ''
        vdelta_frequency_number_string = engineering_units(two_sig_figs(self.get_delta_frequency(hor_setting)))
        if self.vert_visible and vdelta_frequency_number_string is not None:
            vdelta_frequency: str = vdelta_frequency_number_string + 'Hz' 
        else:
            vdelta_frequency = ''
        return { 'h1': h1, 'h2': h2, 'hdelta': hdelta, 'v1': v1, 'v2': v2, 'vdelta': vdelta, '1/vdelta': vdelta_frequency }