from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont 

from voltpeek import constants

@dataclass
class ExportSettings:
    vertical_setting: float
    horizontal_setting: float
    probe_div: int
    map: list[list[tuple[int]]]

def export_png(settings: ExportSettings, filename: str):
    flat_map = []
    for row in settings.map:
        flat_map += row
    image = Image.new('RGB', (constants.Display.SIZE, constants.Display.SIZE))
    image.putdata(flat_map) 
    # TODO: make the font universal
    font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf', 20)
    draw = ImageDraw.Draw(image)
    draw.text((10, 5), str(settings.vertical_setting*settings.probe_div) + ' V/div', font=font)
    draw.text((10, 30), str(settings.horizontal_setting) + ' s/div', font=font)
    draw.text((10, 55), 'Probe: ' + str(settings.probe_div) + 'X', font=font)
    image.save(filename + '.png')