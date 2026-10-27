import cv2
import numpy as np
from app.image_processor import affine_matrix, composite

class ClothingEngine:
    def __init__(self, catalog):
        self.catalog = catalog

    def render(self, frame, points, outfit, scale):
        h, w = frame.shape[:2]
        p = points[:, :2] * [w, h]
        output = frame.copy()
        for layer in outfit['layers']:
            indices = (11, 12, 23, 24) if layer['kind'] == 'upper' else (23, 24, 27, 28)
            if np.min(points[list(indices), 3]) < .45:
                continue
            # Sorting in screen coordinates also supports mirrored input.
            top = sorted([p[indices[0]], p[indices[1]]], key=lambda v: v[0])
            bottom = (p[indices[2]] + p[indices[3]])/2
            targets = [top[0], top[1], bottom]
            if np.linalg.norm(top[1]-top[0]) < 12:
                continue
            asset = self.catalog.cache[layer['asset']]
            matrix = affine_matrix(layer['anchors'], (asset.shape[1], asset.shape[0]), targets, scale*layer.get('scale',1.0))
            output = composite(output, asset, matrix)
        # Approximate forearm occlusion, restricted to reliable landmarks.
        mask = np.zeros((h, w), np.uint8)
        thickness = max(6, int(np.linalg.norm(p[11]-p[12])*.12))
        for a, b in ((13, 15), (14, 16)):
            if min(points[a, 3], points[b, 3]) > .65:
                cv2.line(mask, tuple(p[a].astype(int)), tuple(p[b].astype(int)), 255, thickness, cv2.LINE_AA)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        covered = mask > 0
        weight = mask[covered].astype(np.float32)[:,None]/255
        output[covered] = (output[covered]*(1-weight) + frame[covered]*weight).astype(np.uint8)
        return output
