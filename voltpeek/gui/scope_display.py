from typing import Optional

import tkinter as tk
from scipy.interpolate import interp1d

from voltpeek import constants 
from voltpeek.cursors import Cursors, Selected_Cursor

from voltpeek.trigger import TriggerType

class Scope_Display:
    BACKGROUND_COLOR = (0, 0, 0)
    GRID_LINE_COLOR = (128, 128, 128)
    SIGNAL_COLOR = (17, 176, 249)
    MAX_TRIGGER_CORRECTION_PIXELS: int = 6
    DASH_PATTERN = (4, 2) # 4 pixels on 2 off

    COURSE_STEP = 10
    FINE_STEP = 1

    def _hex_string_from_rgb(self, rgb: tuple[int]): return '#%02x%02x%02x' % rgb

    def __init__(self, master, cursors) -> None:
        self.master:tk.Tk = master        
        self.frame = tk.Frame(self.master)
        self.canvas = tk.Canvas(self.frame, height=constants.Display.SIZE, width=constants.Display.SIZE, 
                                bg=self._hex_string_from_rgb(self.BACKGROUND_COLOR))
        self._draw_grid()
        self.vector:Optional[list[int]] = None
        self.cursors:Optional[Cursors] = cursors
        self._trigger_level = 0

    def __call__(self):
        self.canvas.pack()
        self.frame.grid(row=0, column=0, pady=constants.Application.PADDING)

    def _draw_grid(self) -> None:
        grid_spacing:int = int(constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        for i in range(1, constants.Display.GRID_LINE_COUNT+1):
            # Draw Vertical Grid Lines
            self.canvas.create_line(grid_spacing*i, 0, grid_spacing*i, constants.Display.SIZE, 
                                    fill=self._hex_string_from_rgb(self.GRID_LINE_COLOR))
            # Draw Horizontal Grid Lines
            self.canvas.create_line(0, grid_spacing*i,  constants.Display.SIZE, grid_spacing*i, 
                                    fill=self._hex_string_from_rgb(self.GRID_LINE_COLOR))
                        
    def _quantize_vertical(self, vertical_setting: float) -> list[int]:
        pixel_amplitude: float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        pixel_resolution: float = vertical_setting/pixel_amplitude
        self.vector = [int(v/pixel_resolution) + int(constants.Display.SIZE/2) for v in self.vector] 

    def _resample_horizontal(self, hor_setting: float, vert_setting: float, 
                             fs: float, memory_depth: int, edge: TriggerType, 
                             triggered: bool) -> list[int]:
        tt:list[float] = [i/fs for i in range(0, len(self.vector))]
        f = interp1d(tt, self.vector, kind='linear', fill_value=0, bounds_error=False)
        new_T: float = (hor_setting)/(constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        chop_time: float = (1/fs)*memory_depth - hor_setting*constants.Display.GRID_LINE_COUNT
        grid_size: float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        vertical_pixel_amplitude: float = vert_setting/grid_size
        horizontal_pixel_time: float = hor_setting/grid_size
        set_trigger_voltage: float = self.get_trigger_voltage(vert_setting)
        centered_vector: list[float] = f([(i*new_T) + (chop_time/2) for i in range(0, constants.Display.SIZE)])   
        if triggered:
            # This obviously needs to be refactored
            delta_time: float = 0
            i = 0
            if edge == TriggerType.RISING_EDGE:
                captured_trigger_voltage: float = centered_vector[(constants.Display.SIZE//2)+1]
                if captured_trigger_voltage > set_trigger_voltage:
                    while captured_trigger_voltage > set_trigger_voltage:
                        if i > constants.Display.SIZE//4:
                            delta_time = 0
                            break
                        captured_trigger_voltage = centered_vector[(constants.Display.SIZE//2)+1-i]
                        delta_time -= horizontal_pixel_time
                        i += 1
                    if abs(set_trigger_voltage - captured_trigger_voltage) > self.MAX_TRIGGER_CORRECTION_PIXELS*vertical_pixel_amplitude:
                        delta_time = 0
                if captured_trigger_voltage < set_trigger_voltage:
                    while captured_trigger_voltage < set_trigger_voltage:
                        if i > constants.Display.SIZE//4:
                            delta_time = 0
                            break
                        captured_trigger_voltage = centered_vector[(constants.Display.SIZE//2)+1+i]
                        delta_time += horizontal_pixel_time
                        i += 1
                    if abs(set_trigger_voltage - captured_trigger_voltage) > self.MAX_TRIGGER_CORRECTION_PIXELS*vertical_pixel_amplitude:
                        delta_time = 0
            elif edge == TriggerType.FALLING_EDGE:
                captured_trigger_voltage: float = centered_vector[(constants.Display.SIZE//2)+1]
                if captured_trigger_voltage > set_trigger_voltage:
                    while captured_trigger_voltage > set_trigger_voltage:
                        if i > constants.Display.SIZE//4:
                            delta_time = 0
                            break
                        captured_trigger_voltage = centered_vector[(constants.Display.SIZE//2)+1+i]
                        delta_time += horizontal_pixel_time
                        i += 1
                    if abs(set_trigger_voltage - captured_trigger_voltage) > self.MAX_TRIGGER_CORRECTION_PIXELS*vertical_pixel_amplitude:
                        delta_time = 0
                if captured_trigger_voltage < set_trigger_voltage:
                    while captured_trigger_voltage < set_trigger_voltage:
                        if i > constants.Display.SIZE//4:
                            delta_time = 0
                            break
                        captured_trigger_voltage = centered_vector[(constants.Display.SIZE//2)+1-i]
                        delta_time -= horizontal_pixel_time
                        i += 1
                    if abs(set_trigger_voltage - captured_trigger_voltage) > self.MAX_TRIGGER_CORRECTION_PIXELS*vertical_pixel_amplitude:
                        delta_time = 0
            self.vector = f([(i*new_T) + (chop_time/2) + delta_time for i in range(0, constants.Display.SIZE)])
        else:
            self.vector = centered_vector

    def resample_vector(self, hor_setting: float, vert_setting: float, 
                        fs: float, memory_depth: int, edge: TriggerType, 
                        triggered: bool) -> None:
        if len(self.vector) == memory_depth:
            # Horizontal resampling must be done before vertical quantization because amplitude information is 
            # needed for trigger point interpolation.
            self._resample_horizontal(hor_setting, vert_setting, fs, memory_depth, edge, triggered)
            self._quantize_vertical(vert_setting)
            self._redraw()

    def set_cursors(self, cursors: Cursors):
        self.cursors = cursors
        self._redraw()

    def set_vector(self, vector: list[int]): self.vector = vector

    def set_trigger_level(self, trigger_level) -> None:
        self._trigger_level: int = trigger_level
        self._redraw()
        self._draw_trigger_level()

    def get_trigger_voltage(self, vertical_setting: float) -> float:
        pixel_division:float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        pixel_resolution:float = vertical_setting/pixel_division
        return float((constants.Display.SIZE - self._trigger_level - (constants.Display.SIZE/2))*pixel_resolution)

    def _increment_trigger_level(self, count) -> None:
        if self._trigger_level < constants.Display.SIZE - count:
            self.set_trigger_level(self._trigger_level - count)

    def _decrement_trigger_level(self, count) -> None:
        if self._trigger_level > count:
            self.set_trigger_level(self._trigger_level + count)

    def increment_trigger_level_fine(self) -> None: self._increment_trigger_level(self.FINE_STEP) 

    def decrement_trigger_level_fine(self) -> None: self._decrement_trigger_level(self.FINE_STEP)

    def increment_trigger_level_course(self) -> None: self._increment_trigger_level(self.COURSE_STEP)

    def decrement_trigger_level_course(self) -> None: self._decrement_trigger_level(self.COURSE_STEP)

    def _draw_horizontal_cursors(self) -> None:
        if self.cursors.selected_cursor == Selected_Cursor.HOR1:
            self._draw_dashed_horizontal_line(self.cursors.hor1_pos, constants.Display.CURSOR_COLOR)
        else:
            self._draw_horizontal_line(self.cursors.hor1_pos, constants.Display.CURSOR_COLOR)  

        if self.cursors.selected_cursor == Selected_Cursor.HOR2:
            self._draw_dashed_horizontal_line(self.cursors.hor2_pos, constants.Display.CURSOR_COLOR)
        else:
            self._draw_horizontal_line(self.cursors.hor2_pos, constants.Display.CURSOR_COLOR)

    def _draw_vertical_cursors(self) -> None:
        if self.cursors.selected_cursor == Selected_Cursor.VERT1:
            self._draw_dashed_vertical_line(self.cursors.vert1_pos, constants.Display.CURSOR_COLOR)
        else:
            self._draw_vertical_line(self.cursors.vert1_pos, constants.Display.CURSOR_COLOR)
        
        if self.cursors.selected_cursor == Selected_Cursor.VERT2:
            self._draw_dashed_vertical_line(self.cursors.vert2_pos, constants.Display.CURSOR_COLOR)
        else:
            self._draw_vertical_line(self.cursors.vert2_pos, constants.Display.CURSOR_COLOR)

    def _redraw(self) -> None:
        self.canvas.delete('all')
        self._draw_grid()
        if self.vector is not None:
            self._draw_vector()
        if self.cursors.hor_visible:
            self._draw_horizontal_cursors()
        if self.cursors.vert_visible:
            self._draw_vertical_cursors()
        self._draw_trigger_level()

    def _draw_vector(self):
        for i, point in enumerate(self.vector):
            if point > 0: 
                if i < len(self.vector) - 1:
                    next_point: int = self.vector[i+1]
                    self.canvas.create_line(i-1, constants.Display.SIZE - point, i+2, 
                                            constants.Display.SIZE - next_point, 
                                            fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))
                    self.canvas.create_line(i-1, constants.Display.SIZE - point + 1, i+2, 
                                            constants.Display.SIZE - next_point + 1, 
                                            fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))
                    self.canvas.create_line(i-1, constants.Display.SIZE - point - 1, i+2, 
                                            constants.Display.SIZE - next_point-1, 
                                            fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))
                else:
                    self.canvas.create_line(i-1, constants.Display.SIZE - point, i+2, 
                                            constants.Display.SIZE - point, 
                                            fill=self._hex_string_from_rgb(self.SIGNAL_COLOR)) 
                    self.canvas.create_line(i-1, constants.Display.SIZE - point + 1, i+2, 
                                            constants.Display.SIZE - point + 1, 
                                            fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))
                    self.canvas.create_line(i-1, constants.Display.SIZE - point - 1, i+2, 
                                            constants.Display.SIZE - point-1, 
                                            fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))

    def _draw_dashed_horizontal_line(self, position, color):
        self.canvas.create_line(0, position, constants.Display.SIZE, position, fill=color, dash=self.DASH_PATTERN)
    
    def _draw_horizontal_line(self, position, color): 
        self.canvas.create_line(0, position, constants.Display.SIZE, position, fill=color)

    def _draw_dashed_vertical_line(self, position, color):
        self.canvas.create_line(position, 0, position, constants.Display.SIZE, fill=color, dash=self.DASH_PATTERN)

    def _draw_vertical_line(self, position, color): 
        self.canvas.create_line(position, 0, position, constants.Display.SIZE, fill=color)

    def _draw_trigger_level(self): self._draw_horizontal_line(self._trigger_level, constants.Display.TRIGGER_LINE_COLOR)

    @property
    def image_map(self):
        map: list[list[tuple[int]]] = [[self.BACKGROUND_COLOR for _ in range(0, constants.Display.SIZE)] 
                                       for _ in range(0, constants.Display.SIZE)]
        grid_spacing: int = int(constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        # Draw the grid lines.
        for y, row in enumerate(map):
            for x, _ in enumerate(row):
                if y % grid_spacing == 0 or x % grid_spacing == 0 or x == len(map) - 1 or y == len(row) - 1:
                    map[y][x] = self.GRID_LINE_COLOR
        # Draw the signal.
        if self.vector is not None:
            for x, point in enumerate(self.vector):
                for x_padding in range(-1, 2):
                    for y_padding in range(-1, 2):
                        y_point: int = constants.Display.SIZE - int(point) + y_padding
                        x_point: int = int(x) + x_padding
                        if y_point >= 0 and y_point < constants.Display.SIZE and x_point >= 0 and x_point < constants.Display.SIZE: 
                            map[y_point][x_point] = self.SIGNAL_COLOR 
        return map