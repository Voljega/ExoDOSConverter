import math
from PIL import Image, ImageDraw
from PIL.ImageTk import PhotoImage

SUPERSAMPLING = 4  # images are drawn bigger then reduced to get smooth edges


def mix(color, other, ratio):
    """Color between two '#rrggbb' colors, ratio 0 gives color and 1 gives other"""
    channels = [round(int(color[i:i + 2], 16) * (1 - ratio) + int(other[i:i + 2], 16) * ratio) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(channels)


def gearButtonColors(style):
    """Background of the gear button while the settings are open, the theme draws it like any other flat button"""
    selected = mix(style.colors.bg, style.colors.border, 0.5)
    style.master.tk.call('ttk::style', 'map', 'Toolbutton', '-background', ['selected', selected])
    # the themes don't give the same padding around the icon, which would not be centered the same way
    style.master.tk.call('ttk::style', 'configure', 'Toolbutton', '-padding', [6, 0])


def closeIcon(color, size=14):
    """Cross in the given '#rrggbb' color, same size as the gear it replaces while the settings are open"""
    scale = 8 * SUPERSAMPLING
    side = size * scale
    margin = 0.2 * side
    image = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    width = round(0.14 * side)
    draw.line((margin, margin, side - margin, side - margin), fill=color, width=width)
    draw.line((margin, side - margin, side - margin, margin), fill=color, width=width)
    return PhotoImage(image.resize((size, size), Image.LANCZOS))


def gearIcon(color, size=14, teeth=8):
    """Gear in the style of the Material Design settings icon, drawn in the given '#rrggbb' color"""
    scale = 8 * SUPERSAMPLING
    side = size * scale
    center = side / 2
    image = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    body, tip, hole = 0.70 * center, 0.98 * center, 0.30 * center
    draw.ellipse((center - body, center - body, center + body, center + body), fill=color)
    for index in range(teeth):
        angle = 2 * math.pi * index / teeth
        points = []
        # each tooth is a trapezoid, wider at its root inside the body than at its tip
        for radius, halfWidth in ((body * 0.8, 0.20), (tip, 0.12), (tip, -0.12), (body * 0.8, -0.20)):
            offset = angle + halfWidth
            points.append((center + radius * math.cos(offset), center + radius * math.sin(offset)))
        draw.polygon(points, fill=color)
    draw.ellipse((center - hole, center - hole, center + hole, center + hole), fill=(0, 0, 0, 0))
    return PhotoImage(image.resize((size, size), Image.LANCZOS))
