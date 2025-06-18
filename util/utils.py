import math
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

R = 6371000  # 지구 반지름

# 두 지점의 위도(lat), 경도(lon) 좌표를 받아, 지구상의 대원거리를 미터 단위로 계산해 반환
# 반환값은 두 점 사이의 거리(미터)
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2) # 위도를 라디안으로 변환

    # Δ위도, Δ경도(라디안)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2) ** 2 # haversine 공식을 위한 중간값 a 계산

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) # 대원거리 계산

from dataclasses import dataclass
@dataclass
class GPSData:
    latitude: float
    longitude: float
    altitude: float
    timestamp: datetime