"""Generate original geometric demo assets, not authentic costume reproductions."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]

def generate():
    root = ROOT/'assets/clothes'
    root.mkdir(parents=True, exist_ok=True)
    definitions = [
        ('heritage','Heritage / Men','បុរស / គំរូ','Traditional men','male','#244d82','#d8b76b'),
        ('silk','Silk / Women','ស្ត្រី / គំរូ','Traditional women','female','#854b79','#e6c38a'),
        ('wedding','Golden ceremony','អាពាហ៍ពិពាហ៍ / គំរូ','Wedding','unisex','#c29c4b','#fff0ba'),
        ('sampot','Sampot study','សំពត់ / គំរូ','Silk sampot','unisex','#216a6b','#ceba81'),
        ('ceremony','Midnight ceremony','ពិធី / គំរូ','Ceremonial','male','#3c3977','#d8b56d'),
        ('apsara','Apsara study','អប្សរា / គំរូ','Apsara-inspired','female','#a76b4d','#eed090'),
        ('modern','Modern indigo','សម័យថ្មី / គំរូ','Modern Khmer-inspired','unisex','#32466f','#76d7dd')]
    items = []
    for ident, name, km, category, gender, color, gold in definitions:
        folder = root/gender
        folder.mkdir(exist_ok=True)
        layers = []
        thumb = Image.new('RGBA',(400,640))
        for kind in ('upper','lower'):
            image = Image.new('RGBA',(400,480))
            draw = ImageDraw.Draw(image)
            if kind == 'upper':
                polygon = [(90,60),(150,45),(175,80),(225,80),(250,45),(310,60),
                           (365,155),(305,185),(285,400),(115,400),(95,185),(35,155)]
                anchors = [[.225,.125],[.775,.125],[.5,.83]]
            else:
                polygon = [(100,35),(300,35),(325,450),(75,450)]
                anchors = [[.25,.073],[.75,.073],[.5,.94]]
            draw.polygon(polygon, fill=color, outline=gold, width=6)
            mask = image.getchannel('A')
            pattern = Image.new('RGBA', image.size)
            pen = ImageDraw.Draw(pattern)
            for y in range(70,460,34):
                for x in range(55,355,34):
                    pen.polygon([(x,y-5),(x+5,y),(x,y+5),(x-5,y)], fill=gold+'a0')
            pattern.putalpha(Image.composite(pattern.getchannel('A'), Image.new('L',image.size), mask))
            image = Image.alpha_composite(image, pattern)
            draw = ImageDraw.Draw(image)
            if kind == 'lower':
                draw.rectangle((100,35,300,58),fill=gold)
                draw.line((220,60,245,440),fill=gold,width=5)
            path = folder/f'{ident}_{kind}.png'
            if not path.exists():
                image.save(path)
            layers.append(dict(kind=kind, asset=path.relative_to(root).as_posix(), anchors=anchors, scale=1.0))
            preview = image.resize((280,336))
            thumb.alpha_composite(preview,(60,0 if kind=='upper' else 280))
        thumbnail = folder/f'{ident}_thumb.png'
        if not thumbnail.exists():
            thumb.save(thumbnail)
        items.append(dict(id=ident,name=name,name_km=km,category=category,gender=gender,
                          placeholder=True,thumbnail=thumbnail.relative_to(root).as_posix(),layers=layers))
    catalog = root/'catalog.json'
    if not catalog.exists():
        catalog.write_text(json.dumps(items,indent=2,ensure_ascii=False),'utf-8')
    for folder in ('icons','backgrounds','fonts'):
        (ROOT/'assets'/folder).mkdir(exist_ok=True)
    print('Illustrative clothing assets ready.')

if __name__ == '__main__':
    generate()
