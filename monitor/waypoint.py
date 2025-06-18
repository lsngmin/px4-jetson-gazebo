from common.singleton_mixin import SingletonMixin
from monitor.interface.monitor_interface import MonitorInterface
from util.location import Location


class WaypointMonitor(MonitorInterface, SingletonMixin):
    def __init__(self):
        super().__init__()
        SingletonMixin.__init__(self)
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

    def set_trigger_callback(self, callback):
        self._on_condition_callback = callback

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
            status = "목표 반경 진입" if self._inside else "목표 반경 이탈"
            self._logger.info(
                f"[WaypointMonitor] {status}: 반경 {self.radius_m}m, "
                f"연속 {self.hold_count}회, 거리 {distance:.2f}m"
            )
            # 콜백 호출 (진입/이탈 모두 반영)
            if self._on_condition_callback:
                self._on_condition_callback(self._inside)

    def _get_monitor_config(self):
        return (
            'GLOBAL_POSITION_INT',
            f"위치 모니터 시작 — 목표:({self._target_location.lat},{self._target_location.lon}), 반경:{self.radius_m}m"
        )