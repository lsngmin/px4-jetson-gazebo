import math
from dataclasses import dataclass

R = 6371000  # 지구 반지름(m)

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
