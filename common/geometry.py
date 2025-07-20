import numpy as np

from typing import Tuple
from common.messages import UV
fx, fy = 400.0, 400.0       # 픽셀 단위 초점거리(임의)
cx, cy = 320.0, 240.0       # 주점(프레임 정중앙 가정)

def xywh_to_uv(x:int, y:int, w:int, h:int) -> Tuple[float, float]:
    return float(x), float(y)

def uv_depth_to_cam(uv:UV, depth:float) -> np.ndarray:
    Xc = (uv.u - cx) / fx * depth
    Yc = (uv.v - cy) / fy * depth
    Zc = depth
    return np.array([Xc, Yc, Zc], dtype=float)
