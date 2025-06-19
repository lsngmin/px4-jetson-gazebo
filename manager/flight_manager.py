import threading, time, logging

from pymavlink import mavutil

from common import Singleton
from control.authority import AuthorityControl
from core import MavLinkClient
from manager.check_preflight import CheckPreflight
from monitor.position import PositionMonitor, PositionData

class FlightManager(Singleton):
    def __init__(self):
        self._client = MavLinkClient.get_instance()
        self._config = self._client.config
        self._logger = logging.getLogger(self.__class__.__name__)
        # self._check_preflight = CheckPreflight.get_instance().start()
        self._current = {'x': 0.0, 'y': 0.0, 'z': 0.0}

        self._position_monitor = PositionMonitor.get_instance().start_with_callback(self.on_position_changed)
        self._authority_control = AuthorityControl.get_instance().start_with_callback(self.on_authority_activated)
        self._is_authority_active = False
        self._client.master.wait_heartbeat(timeout=10)
        self._current_position = None


        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._watchdog_thread = threading.Thread(target=self._offboard_watchdog, daemon=True)
        self._watchdog_thread.start()

    def on_position_changed(self, position: PositionData):
        self._current['x'] = position.x
        self._current['y'] = position.y
        self._current['z'] = position.z
        self._current_position = position

    def on_authority_activated(self, is_active: bool):
        if is_active and not self._is_authority_active:
            self._logger.info("자동 비행 제어권(Authority) 획득. (OFFBOARD 진입 준비)")
            for _ in range(20):
                now_ms = int(time.time() * 1000) % 0xFFFFFFFF
                self._client.master.mav.set_position_target_local_ned_send(
                    now_ms, self._client.master.target_system, self._client.master.target_component,
                    mavutil.mavlink.MAV_FRAME_LOCAL_NED, 0b0000111111111000,
                    self._current_position.x, self._current_position.y, self._current_position.z, 0, 0, 0, 0, 0, 0, 0, 0
                )
                time.sleep(0.05)
            self._client.master.set_mode_px4(
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                6,
                0
            )
            self._logger.info("OFFBOARD 모드로 전환 완료. setpoint 스트림 유지 중!")
        self._is_authority_active = is_active

    def get_target(self):
        with self._lock:
            return self._current['x'], self._current['y'], self._current['z']

    def _offboard_watchdog(self, sleep=0.05):
        while not self._stop_event.is_set():
            now_ms = int(time.time() * 1000) % 0xFFFFFFFF
            x, y, z = self.get_target()
            self._client.master.mav.set_position_target_local_ned_send(
                now_ms, self._client.master.target_system, self._client.master.target_component,
                mavutil.mavlink.MAV_FRAME_LOCAL_NED, 0b0000111111111000,
                x, y, z, 0,0,0, 0,0,0, 0,0
            )
            time.sleep(sleep)
