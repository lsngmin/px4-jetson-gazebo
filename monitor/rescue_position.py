from typing_extensions import override

from common import Singleton
from monitor import MonitorInterface
from util import Location

class RescuePositionMonitor(MonitorInterface, Singleton):
    def __init__(self):
        super().__init__()
        self._target_lat = self._config.rescue_target_lat
        self._target_lon = self._config.rescue_target_lon
        self._target_tolerance = self._config.rescue_target_tolerance
        self._on_condition_callback = None
        self._is_rescue_reached = None

    #TODO: GPS 좌표가 어떻게 들어올 지, 어떤 형식으로 들어올 지 아직 모름.
    #TODO: 나중에 확정되면 로직 변경 필요할거 같음
    @override
    def _handle_message(self, msg):
        current_location = Location(lat=msg.lat/1e7, lon=msg.lon/1e7)
        target_location = Location(lat=self._target_lat, lon=self._target_lon)

        distance = current_location.distance_to(target_location)
        reached = distance < self._target_tolerance
        if reached and not self._is_rescue_reached:
            self._logger.info(f"조난자 위치에 도달했습니다. - 반경 {distance:.1f}m")
        elif not reached and self._is_rescue_reached:
            self._logger.info(f"조난자 위치에서 이탈했습니다. - 반경 {distance:.1f}m")

        self._is_rescue_reached = reached

        if callable(self._on_condition_callback):
            self._on_condition_callback(reached)

    @override
    def _register_callback(self, callback):
        self._on_condition_callback = callback

    @override
    def _get_monitor_config(self):
        return (
            'GLOBAL_POSITION_INT',
            f'조난자 위치 도달 감시 활성화 — 목표 위치: ({self._target_lat}, {self._target_lon})'
        )
