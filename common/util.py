import math
from datetime import datetime
from dataclasses import dataclass
import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Location:
    lat: float
    lon: float

    def distance_to(self, other: "Location") -> float:
        """
        Haversine 공식을 이용해 두 Location 객체 사이의 거리를 미터(m) 단위로 반환.
        """
        phi1, phi2 = math.radians(self.lat), math.radians(other.lat)
        dphi = math.radians(other.lat - self.lat)
        dlambda = math.radians(other.lon - self.lon)

        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


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

class PositionData(BaseModel):
    x: float = Field(..., description="현재 x (미터, 북쪽 기준)")
    y: float = Field(..., description="현재 y (미터, 동쪽 기준)")
    z: float = Field(..., description="현재 z (미터, 아래로 증가)")

    @classmethod
    def make(cls, msg):
        return cls(
            x = msg.x,
            y = msg.y,
            z = msg.z
        )