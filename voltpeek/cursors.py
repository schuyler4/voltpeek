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
    def hor1_pos(self): return self._hor1_pos
    @property
    def hor2_pos(self): return self._hor2_pos
    @property
    def vert1_pos(self): return self._vert1_pos
    @property
    def vert2_pos(self): return self._vert2_pos
    @property
    def hor_visible(self): return self._hor_visible
    @property
    def vert_visible(self): return self._vert_visible

    def increment_hor1(self): 
        if(self._hor1_pos < constants.Display.SIZE): self._hor1_pos += 1 
    def decrement_hor1(self): 
        if(self._hor1_pos > 0): self.hor1_pos -= 1
    def increment_hor2(self): 
        if(self._hor2_pos < constants.Display.SIZE): self._hor1_pos += 1
    def decrement_hor2(self): 
        if(self._hor2_pos > 0): self.hor2_pos -= 1
    def increment_vert1(self): 
        if(self._vert1_pos < constants.Display.SIZE): self._vert1_pos += 1
    def decrement_vert2(self): 
        if(self._vert2_pos > 0): self.vert2_pos -= 1

    def toggle_hor(self): 
        self._hor_visible = not self._hor_visible
        self._selected_cursor = Selected_Cursor.HOR1 
    def toggle_vert(self): 
        self._vert_visible = not self._vert_visible
        self._selected_cursor = Selected_Cursor.VERT1 
    def toggle(self):
        self._hor_visible = not self._hor_visible
        self._vert_visible = not self._vert_visible
        self._selected_cursor = Selected_Cursor.HOR1
        print(self._selected_cursor)

    def next_cursor(self): 
        print(self._selected_cursor)
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
