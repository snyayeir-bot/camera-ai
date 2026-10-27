from datetime import datetime
from pathlib import Path
import uuid
import cv2
from PIL import Image, ImageDraw

def prepare_photo(bgr, decorative=True):
    image = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    if decorative:
        draw = ImageDraw.Draw(image)
        w, h = image.size
        draw.rectangle((12, 12, w-13, h-13), outline='#d8b56d', width=4)
        for x in range(32, w-32, 28):
            draw.polygon([(x,h-35),(x+6,h-28),(x,h-21),(x-6,h-28)], fill='#d8b56d')
        draw.rectangle((20, 20, 300, 48), fill='#111827')
        draw.text((30, 28), 'KHMER AI / VIRTUAL TRY-ON / 2D', fill='#f0d59b')
    return image

def save_photo(image, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f'khmer-{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}.png'
    image.save(target)
    return target
