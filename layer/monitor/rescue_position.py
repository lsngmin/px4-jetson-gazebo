from typing_extensions import override

from default import VTOL_STATE_CHANGED, VtolStateEnum, RESCUE_POSITION_HIT

from layer.monitor import Monitor
from common.pattern import Singleton
from common.util import Location

class RescuePositionMonitor(Monitor, Singleton):
    def __init__(self):
        super().__init__('GLOBAL_POSITION_INT')
        self._target_lat = self._config.rescue_target_lat
        self._target_lon = self._config.rescue_target_lon
        self._target_tolerance = self._config.rescue_target_tolerance
        self._is_rescue_reached = None

        self._logger.info(f'조난자 위치 도달 감시 활성화 — 목표 위치: ({self._target_lat}, {self._target_lon})')

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
        self._ed.publish(RESCUE_POSITION_HIT, reached)