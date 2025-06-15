from typing import Optional

import tkinter as tk
from scipy.interpolate import interp1d
import numpy as np
from numpy.typing import NDArray

from voltpeek import constants 

from voltpeek.cursors import Cursors, Selected_Cursor
from voltpeek.trigger import TriggerType

class Scope_Display:
    BACKGROUND_COLOR = (0, 0, 0)
    GRID_LINE_COLOR = (128, 128, 128)
    SIGNAL_COLOR = (17, 176, 249)
    CURSOR_COLOR = (255, 0, 0)  # Added red cursor color
    TRIGGER_COLOR = (255, 255, 255)
    MAX_TRIGGER_CORRECTION_PIXELS: int = 6
    DASH_PATTERN = (4, 2) # 4 pixels on 2 off

    COURSE_STEP = 10
    FINE_STEP = 1

    def _hex_string_from_rgb(self, rgb: tuple[int]): return '#%02x%02x%02x' % rgb

    def __init__(self, master, cursors, size) -> None:
        self.master:tk.Tk = master        
        self._size = size
        self.frame = tk.Frame(self.master)
        self.canvas = tk.Canvas(self.frame, height=self._size, width=self._size, bg=self._hex_string_from_rgb(self.BACKGROUND_COLOR))
        self._draw_grid()
        self._vectors: list[int] = []
        self.cursors: Optional[Cursors] = cursors
        self._trigger_level: int = 0
        self._trigger_set: bool = False
        self.display_vector = []
        self._display_record: list[int] = None
        self._record: list[float] = None
        self._record_index: int = 0

    def __call__(self):
        self.canvas.pack()
        self.frame.grid(row=0, column=0, pady=constants.Application.PADDING, padx=constants.Application.PADDING)

    def _draw_grid(self) -> None:
        grid_spacing:int = int(self._size/constants.Display.GRID_LINE_COUNT)
        for i in range(1, constants.Display.GRID_LINE_COUNT+1):
            # Draw Vertical Grid Lines
            self.canvas.create_line(grid_spacing*i, 0, grid_spacing*i, self._size, fill=self._hex_string_from_rgb(self.GRID_LINE_COLOR))
            # Draw Horizontal Grid Lines
            self.canvas.create_line(0, grid_spacing*i,  self._size, grid_spacing*i, fill=self._hex_string_from_rgb(self.GRID_LINE_COLOR))
                        
    def _quantize_vertical(self, vector: list[float], vertical_setting: float) -> list[int]:
        pixel_resolution: float = vertical_setting/(self._size/constants.Display.GRID_LINE_COUNT)
        return np.add(np.multiply(vector, 1/pixel_resolution), int(self._size/2))

    def _resample_horizontal_vector(self, vector: NDArray[np.float64], hor_setting: float, vert_setting: float, 
                                    fs: float, memory_depth: int, edge: TriggerType, triggered: bool) -> list[int]:
        # Fill value is -100 because the signal can never possibly reach this amplitude. This distinguishes real signal vs out of horizontal capture.
        f = interp1d(np.arange(len(vector))/fs, vector, kind='linear', fill_value=-100, bounds_error=False)
        new_T: float = (hor_setting)/(self._size/constants.Display.GRID_LINE_COUNT)
        chop_time: float = (1/fs)*memory_depth - hor_setting*constants.Display.GRID_LINE_COUNT
        hor_pixel_time: float = hor_setting/(self._size/constants.Display.GRID_LINE_COUNT)
        set_trigger_voltage: float = self.get_trigger_voltage(vert_setting)
        centered_vector: list[float] = f(np.add(np.arange(self._size)*new_T,(chop_time/2)))
        if triggered:
            # Trigger Position Correction
            trigger_crossings = np.where(np.diff(np.sign(np.subtract(centered_vector, set_trigger_voltage))))[0]
            if len(trigger_crossings) > 0:
                error_distance_index = np.abs(trigger_crossings - (self._size//2)+1).argmin()
                error_sign = np.sign(trigger_crossings[error_distance_index] - (self._size//2)+1)
                error_magnitude_time = np.abs(trigger_crossings[error_distance_index] - (self._size//2)+1)*hor_pixel_time 
                if error_sign:
                    return f((np.arange(self._size)*new_T) + (chop_time/2) + error_magnitude_time)
                else:
                    return f((np.arange(self._size)*new_T) + (chop_time/2) - error_magnitude_time)
            return []
        else:
            return centered_vector

    def _resample_horizontal_record(self, vert_setting: float, hor_setting: float):
        self._display_record = self.resample_record(vert_setting)

    def resample_vector(self, hor_setting: float, vert_setting: float, fs: float, memory_depth: int, edge: TriggerType, 
                        triggered: bool, FIR_length: int) -> None:
        for vector in self._vectors:
            if len(vector) == memory_depth-(FIR_length-1):
                # Horizontal resampling must be done before vertical quantization because amplitude information is 
                # needed for trigger point interpolation.
                self.display_vector = self._resample_horizontal_vector(hor_setting, vert_setting, fs, memory_depth-(FIR_length-1), edge, triggered)
                if len(self.display_vector) > 0:
                    self.display_vector = self._quantize_vertical(self.display_vector, vert_setting)
                    self._redraw()

    def resample_record(self, vert_setting: float):
        print(self._record)
        if len(self._record) > 0:
            self._display_record = self._quantize_vertical(self._record, vert_setting)
        self._draw_record()
        return None

    def set_cursors(self, cursors: Cursors):
        self.cursors = cursors
        self._redraw()

    def set_trigger_level(self, trigger_level) -> None:
        self._trigger_level: int = int(trigger_level)
        self._trigger_set = True
        self._redraw()
        self._draw_trigger_level()

    def get_trigger_voltage(self, vertical_setting: float) -> float:
        pixel_resolution:float = vertical_setting/(self._size/constants.Display.GRID_LINE_COUNT)
        return float((self._size - self._trigger_level - (self._size/2))*pixel_resolution)

    def _increment_trigger_level(self, count) -> None:
        if self._trigger_level < self._size - count:
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
        if self.display_vector is not None:
            self._draw_vector()
        if self.cursors.hor_visible:
            self._draw_horizontal_cursors()
        if self.cursors.vert_visible:
            self._draw_vertical_cursors()
        if self._trigger_set:
            self._draw_trigger_level()

    def _draw_vector(self):
        y = self._size - np.array(self.display_vector)
        y_filtered = y[y <= self._size]
        x = np.arange(len(self.display_vector))[y <= self._size]
        coords = np.column_stack((x[1:], y_filtered[:-1], x[1:], y_filtered[1:])).reshape(-1).tolist()
        self.canvas.create_line(*coords, fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))
        self.canvas.create_line(*[c + (0 if i % 2 == 0 else 1) for i, c in enumerate(coords)], fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))
        self.canvas.create_line(*[c - (0 if i % 2 == 0 else 1) for i, c in enumerate(coords)], fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))
        if len(x) > 0:
            last_x, last_y = x[-1], y[-1]
            for offset in [-1, 0, 1]:
                self.canvas.create_line(last_x-1, last_y+offset, last_x+2, last_y+offset, fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))

    def _draw_record(self):
        '''
        self._record_index += len(self._display_record)
        if self._record_index > 1:
            y = self._size - np.array(self._display_record)
            x = self._size - np.arange(self._record_index)
            coords = np.column_stack((x[1:], y[:-1], x[1:], y[1:])).reshape(-1).tolist()
            self.canvas.create_line(*coords, fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))
            self.canvas.create_line(*[c + (0 if i % 2 == 0 else 1) for i, c in enumerate(coords)], fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))
            self.canvas.create_line(*[c - (0 if i % 2 == 0 else 1) for i, c in enumerate(coords)], fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))
        '''
        self._record_index += len(self._display_record)
        self.canvas.create_line(self._size - self._record_index, self._display_record[0], self._size - self._record_index+1, self._display_record[0], 
                                fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))
        print(self._display_record)

    def _draw_dashed_horizontal_line(self, position, color): 
        self.canvas.create_line(0, position, self._size, position, fill=color, dash=self.DASH_PATTERN)
    
    def _draw_horizontal_line(self, position, color): self.canvas.create_line(0, position, self._size, position, fill=color)

    def _draw_dashed_vertical_line(self, position, color):
        self.canvas.create_line(position, 0, position, self._size, fill=color, dash=self.DASH_PATTERN)

    def _draw_vertical_line(self, position, color): self.canvas.create_line(position, 0, position, self._size, fill=color)

    def _draw_trigger_level(self): self._draw_horizontal_line(self._trigger_level, self._hex_string_from_rgb(self.TRIGGER_COLOR))

    @property
    def image_map(self):
        map = np.full((self._size, self._size, 3), self.BACKGROUND_COLOR, dtype=np.uint8)
        # Draw the Grid Lines
        grid_spacing = int(self._size/constants.Display.GRID_LINE_COUNT)
        grid_lines = np.arange(grid_spacing, self._size, grid_spacing)
        map[grid_lines, :] = self.GRID_LINE_COLOR
        map[:, grid_lines] = self.GRID_LINE_COLOR
        # Draw the Signal
        if self.display_vector is not None:
            y = self._size - np.array(self.display_vector)
            y_filtered = y[y <= self._size]
            x = np.arange(len(self.display_vector))[y <= self._size]
            y_indices = y_filtered.astype(int)
            valid_y = (y_indices >= 0) & (y_indices < self._size)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    y_shifted = y_indices[valid_y] + dy
                    x_shifted = x[valid_y] + dx
                    valid_points = (y_shifted >= 0) & (y_shifted < self._size) & (x_shifted >= 0) & (x_shifted < self._size)
                    map[y_shifted[valid_points], x_shifted[valid_points]] = self.SIGNAL_COLOR
            for i in range(len(x)-1):
                if 0 <= x[i] < self._size:
                    y1, y2 = int(y_filtered[i]), int(y_filtered[i+1])
                    y_start = max(0, min(y1, y2))
                    y_end = min(self._size, max(y1, y2))
                    if int(x[i]) > 0 and int(x[i]) < self._size:
                        map[y_start:y_end, int(x[i]) + dx] = self.SIGNAL_COLOR
        # Draw the Cursors
        if self.cursors and self.cursors.hor_visible:
            map[self.cursors.hor1_pos] = self.CURSOR_COLOR
            map[self.cursors.hor2_pos] = self.CURSOR_COLOR
        if self.cursors and self.cursors.vert_visible:
            map[:, self.cursors.vert1_pos] = self.CURSOR_COLOR
            map[:, self.cursors.vert2_pos] = self.CURSOR_COLOR
        # Draw the trigger level
        if self._trigger_set:
            map[self._trigger_level] = self.TRIGGER_COLOR
        return [[(int(r), int(g), int(b)) for r, g, b in row] for row in map]

    # That's not going to work
    def add_vector(self, new_vector: NDArray[np.float64], index: int): self._vectors.append(new_vector)

    @property
    def size(self) -> int: return self._size
        
    @size.setter
    def size(self, value: int) -> None: self._size = value

    @property
    def record(self) -> list[float]: return self._record

    @record.setter
    def record(self, new_record): self._record = new_record