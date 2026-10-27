import json
from pathlib import Path
import cv2
import numpy as np

class ClothingManager:
    def __init__(self, root):
        self.root = Path(root)
        self.items = json.loads((self.root / 'catalog.json').read_text('utf-8'))
        self.cache = {}
        seen = set()
        for item in self.items:
            if item['id'] in seen:
                raise ValueError('Duplicate outfit ID')
            seen.add(item['id'])
            if item['gender'] not in ('male', 'female', 'unisex') or not item['layers']:
                raise ValueError('Invalid outfit metadata')
            for layer in item['layers']:
                path = (self.root / layer['asset']).resolve()
                if not path.is_relative_to(self.root.resolve()):
                    raise ValueError('Asset must be inside clothes directory')
                im = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
                anchors = np.asarray(layer['anchors'], dtype=np.float32)
                if im is None or im.ndim != 3 or im.shape[2] != 4:
                    raise ValueError(f'Expected transparent RGBA PNG: {path}')
                if anchors.shape != (3, 2) or not np.isfinite(anchors).all() or np.any(anchors < 0) or np.any(anchors > 1):
                    raise ValueError('Three normalized anchors required')
                if abs(np.cross(anchors[1]-anchors[0], anchors[2]-anchors[0])) < .001:
                    raise ValueError('Anchors must not be collinear')
                if layer['kind'] not in ('upper', 'lower'):
                    raise ValueError('Unknown layer kind')
                scale = layer.get('scale', 1.0)
                if not isinstance(scale, (int, float)) or not .5 <= scale <= 2:
                    raise ValueError('Layer scale must be between 0.5 and 2')
                self.cache[layer['asset']] = im
