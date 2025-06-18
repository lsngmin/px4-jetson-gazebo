import time
from common.singleton_mixin import SingletonMixin
from monitor.interface.monitor_interface import MonitorInterface

class PositionMonitor(MonitorInterface, SingletonMixin):
    def __init__(self):
        super().__init__()
        SingletonMixin.__init__(self)

        self._last_lat = None

    def set_trigger_callback(self, callback):
        self._on_change_cb = callback

    def _get_monitor_config(self):
        return (
            "GLOBAL_POSITION_INT",
            "위 경 고도 실시간 수신 시작"
        )

    def _handle_message(self, msg):
        lat = msg.lat / 1e7
        lon = msg.lon / 1e7
        alt = msg.alt / 1000.0

        # 필요하다면 간단한 변화량 필터(1 m 이하 차이면 무시)
        if self._last_lat and abs(lat - self._last_lat) < (1 / 111111):
            return
        self._last_lat = lat

        self._logger.info(f"[POS] lat={lat:.7f}, lon={lon:.7f}, alt={alt:.1f} m")