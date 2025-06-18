import yaml, os
from dataclasses import dataclass

from common.singleton_mixin import SingletonMixin


@dataclass
class RescueTarget:
    latitude: float
    longitude: float
    altitude: float
    radius: float
    hold_count: int
@dataclass
class Config(SingletonMixin):
    def __init__(self, rescue_target: RescueTarget):
        SingletonMixin.__init__(self)
        self.rescue_target = rescue_target

    # wp2_lat: float
    # wp2_lon: float
    # trigger_radius_m: float
    # trigger_count: int    # 또는 duration_s
    # position_check_rate_hz: float
    # offboard_rate_hz: float
    # ... 기타 MAVLink/ROS2 설정 .. .

    @classmethod
    def from_yaml(cls, path: str):
        if cls._instance is not None:
            return cls._instance  # 이미 있으면 반환

        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        rt = data['rescue_target']
        if not isinstance(rt, RescueTarget):
            rescue_target = RescueTarget(**rt)
        else:
            rescue_target = rt
        return cls.get_instance(rescue_target)
