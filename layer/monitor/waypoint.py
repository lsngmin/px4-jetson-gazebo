from typing_extensions import override

from default import VTOL_STATE_CHANGED, VtolStateEnum

from layer.monitor import Monitor
from common.pattern import Singleton
from common.util import Location

class WaypointMonitor(Monitor, Singleton):
    def __init__(self):
        super().__init__('GLOBAL_POSITION_INT')

        self._on_condition_callback = None
        # 초기화 할 때 조난자 위치의 좌표를 입력 초기화 해야 목표 위치가 업데이트.
        self._target_location = Location(
            self._config.rescue_target.latitude,
            self._config.rescue_target.longitude
        )
        self.radius_m = self._config.rescue_target.radius
        self.hold_count = self._config.rescue_target.hold_count

        self._counter = 0
        self._inside = False
        self._logger.info(f"위치 모니터 시작 — 목표:({self._target_location.lat},{self._target_location.lon}), 반경:{self.radius_m}m")

    @override
    def _handle_message(self, msg):
        current = Location(msg.lat, msg.lon)
        distance = current.distance_to(self._target_location)
        was_inside = self._inside

        if distance <= self.radius_m:
            self._counter += 1
            if self._counter >= self.hold_count:
                self._inside = True
        else:
            self._counter = 0
            self._inside = False

        if was_inside != self._inside:
            # status = "목표 반경 진입" if self._inside else "목표 반경 이탈"
            self._logger.info(
                "[WaypointMonitor] {status}: 반경 {self.radius_m}m, "
                "연속 {self.hold_count}회, 거리 {distance:.2f}m"
            )
            # 콜백 호출 (진입/이탈 모두 반영)
            if self._on_condition_callback:
                #TODO ed publish (self._inside)
                pass
