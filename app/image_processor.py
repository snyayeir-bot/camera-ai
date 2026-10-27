import cv2
import numpy as np

def affine_matrix(anchors, size, targets, scale=1.0):
    source = np.asarray(anchors, np.float32) * np.asarray(size, np.float32)
    target = np.asarray(targets, np.float32)
    center = target.mean(axis=0)
    target = center + (target-center)*scale
    return cv2.getAffineTransform(source, target.astype(np.float32))

def composite(frame, rgba, matrix):
    # Premultiplied alpha avoids dark fringes during interpolation.
    h, w = rgba.shape[:2]
    corners = np.array([[0,0,1],[w,0,1],[0,h,1],[w,h,1]],np.float32) @ matrix.T
    left, top = np.maximum(np.floor(corners.min(axis=0))-1, [0,0]).astype(int)
    right, bottom = np.minimum(np.ceil(corners.max(axis=0))+1, [frame.shape[1],frame.shape[0]]).astype(int)
    if right <= left or bottom <= top:
        return frame.copy()
    local_matrix = matrix.copy()
    local_matrix[:,2] -= [left,top]
    alpha = rgba[:, :, 3:4].astype(np.float32)/255
    premult = np.concatenate((rgba[:, :, :3]*alpha, alpha), axis=2)
    warped = cv2.warpAffine(premult, local_matrix, (right-left,bottom-top))
    output = frame.copy()
    output[top:bottom,left:right] = np.clip(warped[:, :, :3] + frame[top:bottom,left:right]*(1-warped[:, :, 3:4]), 0, 255).astype(np.uint8)
    return output
