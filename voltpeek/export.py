from dataclasses import dataclass
from tkinter import filedialog

from PIL import Image, ImageDraw, ImageFont 

from voltpeek.cursors import Cursor_Data

@dataclass
class ExportSettings:
    vertical_setting: float
    horizontal_setting: float
    probe_div: int
    map: list[list[tuple[int]]]
    cursor_data: Cursor_Data

def export_png(settings: ExportSettings, filename: str, image_size: int):
    flat_map = []
    for row in settings.map:
        flat_map += row
    image = Image.new('RGB', (image_size, image_size))
    image.putdata(flat_map) 
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)
    y_offset = 5
    draw.text((10, y_offset), str(settings.vertical_setting*settings.probe_div) + ' V/div', font=font, fill='white')
    draw.text((10, y_offset + 10), str(settings.horizontal_setting) + ' s/div', font=font, fill='white')
    draw.text((10, y_offset + 20), 'Probe: ' + str(settings.probe_div) + 'X', font=font, fill='white')
    y_offset = 45  # Start cursor readouts below settings
    for key, value in settings.cursor_data.items():
        if value:
            draw.text((10, y_offset), f"{key}: {value}", font=font, fill='white')
            y_offset += 10
    save_path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG files', '*.png')], initialfile=filename+'.png')
    if save_path:
        image.save(save_path)