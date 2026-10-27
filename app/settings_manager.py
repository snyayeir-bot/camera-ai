import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = dict(camera=0, width=1280, height=720, mirror=True, language='en',
                sensitivity=0.55, clothing_scale=1.08, photo_dir='photos',
                inference_width=640, hand_interval=3, fullscreen=False,
                idle_seconds=20, frame=True)

def validate(data):
    result = DEFAULTS | data
    for key, low, high in [('camera', 0, 20), ('width', 320, 1920), ('height', 240, 1080),
                           ('inference_width', 256, 1280), ('hand_interval', 1, 10),
                           ('idle_seconds', 5, 300)]:
        if type(result[key]) is not int or not low <= result[key] <= high:
            raise ValueError(f'Invalid setting: {key}')
    for key, low, high in [('sensitivity', .2, .95), ('clothing_scale', .7, 1.5)]:
        if not isinstance(result[key], (float, int)) or not low <= result[key] <= high:
            raise ValueError(f'Invalid setting: {key}')
    if result['language'] not in ('en', 'km'):
        raise ValueError('Unsupported language')
    for key in ('mirror', 'fullscreen', 'frame'):
        if type(result[key]) is not bool:
            raise ValueError(f'Invalid setting: {key}')
    if not isinstance(result['photo_dir'], str) or not result['photo_dir'].strip():
        raise ValueError('Photo directory is required')
    return result

class Settings:
    def __init__(self, path=None):
        self.path = Path(path or ROOT / 'config.json')
        self.data = validate(json.loads(self.path.read_text('utf-8')) if self.path.exists() else {})

    def save(self, data):
        data = validate(data)
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps(data, indent=2, ensure_ascii=False), 'utf-8')
        temp.replace(self.path)
        self.data = data
