from enum import Enum

from voltpeek import constants

class Selected_Cursor(Enum):
    HOR1 = 0
    HOR2 = 1
    VERT1 = 2
    VERT2 = 3

class Cursors:
    CURSOR_COUNT = 4

    def __init__(self) -> None:
        self._hor1_pos:int = 10  
        self._hor2_pos:int = 20
        self._vert1_pos:int = 10
        self._vert2_pos:int = 20
        self._hor_visible:bool = False
        self._vert_visible:bool = False
        self._selected_cursor = Selected_Cursor.HOR1

    @property
    def hor1_pos(self) -> None: return self._hor1_pos

    @property
    def hor2_pos(self) -> None: return self._hor2_pos

    @property
    def vert1_pos(self) -> None: return self._vert1_pos

    @property
    def vert2_pos(self) -> None: return self._vert2_pos

    @property
    def hor_visible(self) -> None: return self._hor_visible

    @property
    def vert_visible(self) -> None: return self._vert_visible

    def _increment_hor1(self) -> None: 
        if(self._hor1_pos < constants.Display.SIZE): self._hor1_pos += 1 
    
    def _decrement_hor1(self) -> None: 
        if(self._hor1_pos > 0): self._hor1_pos -= 1

    def _increment_hor2(self) -> None: 
        if(self._hor2_pos < constants.Display.SIZE): self._hor2_pos += 1

    def _decrement_hor2(self) -> None: 
        if(self._hor2_pos > 0): self._hor2_pos -= 1

    def _increment_vert1(self) -> None: 
        if(self._vert1_pos < constants.Display.SIZE): self._vert1_pos += 1

    def _decrement_vert1(self) -> None:
        if(self._vert1_pos > 0): self._vert1_pos -= 1

    def _increment_vert2(self) -> None:
        if(self._vert1_pos < constants.Display.SIZE): self._vert2_pos += 1

    def _decrement_vert2(self) -> None: 
        if(self._vert2_pos > 0): self._vert2_pos -= 1

    def increment_hor(self) -> None:
        print(self._selected_cursor)
        if(self._selected_cursor == Selected_Cursor.HOR1):
            self._increment_hor1()
        elif(self._selected_cursor == Selected_Cursor.HOR2):
            self._increment_hor2()

    def decrement_hor(self) -> None:
        if(self._selected_cursor == Selected_Cursor.HOR1):
            self._decrement_hor1()
        elif(self._selected_cursor == Selected_Cursor.HOR2):
            self._decrement_hor2()

    def increment_vert(self) -> None:
        if(self._selected_cursor == Selected_Cursor.VERT1):
            self._increment_vert1()
        elif(self._selected_cursor == Selected_Cursor.VERT2):
            self._increment_vert2()

    def decrement_vert(self) -> None:
        if(self._selected_cursor == Selected_Cursor.VERT1):
            self._decrement_vert1()
        elif(self._selected_cursor == Selected_Cursor.VERT2):
            self._decrement_vert2()

    def toggle_hor(self) -> None: 
        self._hor_visible = not self._hor_visible
        self._selected_cursor = Selected_Cursor.HOR1 

    def toggle_vert(self) -> None: 
        self._vert_visible = not self._vert_visible
        self._selected_cursor = Selected_Cursor.VERT1 

    def toggle(self) -> None:
        self._hor_visible = not self._hor_visible
        self._vert_visible = not self._vert_visible
        self._selected_cursor = Selected_Cursor.HOR1

    def next_cursor(self) -> None: 
        if(self._selected_cursor.value < self.CURSOR_COUNT - 1 
           and self._hor_visible and self._vert_visible): 
            self._selected_cursor = Selected_Cursor(self._selected_cursor.value + 1)        
        elif(self._hor_visible and self._selected_cursor.value < 1):
            self._selected_cursor = Selected_Cursor(self._selected_cursor.value + 1)        
        elif(self._vert_visible and self._selected_cursor.value < self.CURSOR_COUNT - 1):
            self._selected_cursor = Selected_Cursor(self._selected_cursor.value + 1)        
        elif(self._hor_visible):
            self._selected_cursor = Selected_Cursor.HOR1
        elif(self._vert_visible):
            self._selected_cursor = Selected_Cursor.VERT1

    def _get_hor_voltage(self, vertical_setting:float, cursor_height:int) -> float:
        pixel_amplitude:float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        pixel_resolution:float = vertical_setting/pixel_amplitude
        return int(cursor_height/pixel_resolution) + constants.Display.SIZE/2

    def _get_vert_time(self, horizontal_setting:float, cursor_offset:int):
        pixel_offset:float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        pixel_resolution:float = horizontal_setting/pixel_offset
        return int(cursor_offset/pixel_resolution)

    def get_hor1_voltage(self, vertical_setting:float) -> float:
        return self._get_hor_voltage(vertical_setting, self._hor1_pos)

    def get_hor2_voltage(self, vertical_setting:float) -> float:
        return self._get_hor_voltage(vertical_setting, self._hor2_pos)

    def get_delta_voltage(self, vertical_setting:float):
        return self.get_hor1_voltage(vertical_setting) - self.get_hor2_voltage(vertical_setting)

    def get_vert1_time(self, horizontal_setting:float):
        return self._get_vert_time(horizontal_setting, self._vert1_pos)

    def get_vert2_time(self, horizontal_setting:float):
        return self._get_vert_time(horizontal_setting, self._vert2_pos)

    def get_delta_time(self, horizontal_setting:float):
        return self.get_vert1_time(horizontal_setting) - self.get_vert2_time(horizontal_setting)
