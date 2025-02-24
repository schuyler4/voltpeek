from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont 

from voltpeek import constants
from voltpeek.cursors import Cursor_Data

@dataclass
class ExportSettings:
    vertical_setting: float
    horizontal_setting: float
    probe_div: int
    map: list[list[tuple[int]]]
    cursor_data: Cursor_Data

def export_png(settings: ExportSettings, filename: str):
    print(settings.map)
    flat_map = []
    for row in settings.map:
        flat_map += row
    image = Image.new('RGB', (constants.Display.SIZE, constants.Display.SIZE))
    image.putdata(flat_map) 
    # TODO: make the font universal
    font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf', 20)
    draw = ImageDraw.Draw(image)
    y_offset = 5
    draw.text((10, y_offset), str(settings.vertical_setting*settings.probe_div) + ' V/div', font=font, fill='white')
    draw.text((10, y_offset + 25), str(settings.horizontal_setting) + ' s/div', font=font, fill='white')
    draw.text((10, y_offset + 50), 'Probe: ' + str(settings.probe_div) + 'X', font=font, fill='white')
    y_offset = 100  # Start cursor readouts below settings
    for key, value in settings.cursor_data.items():
        if value:
            draw.text((10, y_offset), f"{key}: {value}", font=font, fill='white')
            y_offset += 25
    image.save(filename + '.png')