from PIL import Image, ImageDraw, ImageFont 

from voltpeek import constants

def export_png(map: list[list[tuple[int]]], vertical_setting: float, horizontal_setting: float, filename: str, probe_div: int):
    flat_map = []
    for row in map:
        flat_map += row
    image = Image.new('RGB', (constants.Display.SIZE, constants.Display.SIZE))
    image.putdata(flat_map) 
    # TODO: make the font universal
    font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf', 20)
    draw = ImageDraw.Draw(image)
    draw.text((10, 5), str(vertical_setting*probe_div) + ' V/div', font=font)
    draw.text((10, 30), str(horizontal_setting) + ' s/div', font=font)
    draw.text((10, 55), 'Probe: ' + str(probe_div) + 'X', font=font)
    image.save(filename + '.png')