import logging, time, threading
from pymavlink import mavutil

from common.core import MavLinkClient
from common.pattern import Streamer
from default import SET_MODE_OFFBOARD
from common.pattern import M2EventDispatcher
from layer.handler import Handler


class Command:
    MAV_CMD_COMPONENT_ARM_DISARM = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM
    MAV_CMD_DO_SET_MODE = mavutil.mavlink.MAV_CMD_DO_SET_MODE
    MAV_MODE_FLAG_CUSTOM_MODE_ENABLED = mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED
    MAV_FRAME_LOCAL_NED = mavutil.mavlink.MAV_FRAME_LOCAL_NED
    def __init__(self):
        self._client = MavLinkClient.get_instance()
        self._config = self._client.config
        self._logger = logging.getLogger(self.__class__.__name__)
        self._toc: M2EventDispatcher = M2EventDispatcher.instance()
        self._streamer = None
        self._lock = threading.Lock()
        self.manager = None

        self._toc.subscribe(SET_MODE_OFFBOARD, self.set_mode_offboard)

        while True:
            hb = self._client.master.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
            if hb and hb.get_srcComponent() == mavutil.mavlink.MAV_COMP_ID_AUTOPILOT1:
                # 이 메시지가 FCU에서 온 진짜 heartbeat
                self._client.master.target_system = hb.get_srcSystem()
                self._client.master.target_component = hb.get_srcComponent()
                break

    #---------------------- 0. 시동 켜기/끄기 커맨드 ----------------------
    def _send_disarm_arm(self, param1: int) -> None:
        # param1: 1=Arm, 0=Disarm
        self._client.master.mav.command_long_send(
            self._client.master.target_system, self._client.master.target_component,
            self.MAV_CMD_COMPONENT_ARM_DISARM,
            0, param1, 0, 0, 0, 0, 0, 0
        )

    #---------------------- 1. 시동켜기 ----------------------
    def arm(self) -> None:
        self._send_disarm_arm(1)
        self._logger.info("기체 시동 완료")

    #---------------------- 2. 시동끄기 ----------------------
    def disarm(self) -> None:
        self._send_disarm_arm(0)
        self._logger.info("기체 시동 끄기 완료")

    #---------------------- 3. 오프보드 전환 ----------------------
    def set_mode_offboard(self, handler: Handler) -> None:
        print("들어오김함")
        self.manager = handler
        if self._streamer is not None:
            self._streamer.stop()
            self._streamer.join()
        self._streamer = Streamer(self).with_manager(handler)
        self._streamer.start()

        self._client.master.set_mode_px4(
            self.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            6, 0
        )
        self._logger.info("기체 Offboard 모드 전환 완료")

    #---------------------- 3. 특정 고도로 상승 ----------------------
    def hold_position_takeoff(self, x, y, z) -> None:
        if self._streamer is not None:
            self._streamer.stop()
            self._streamer.join()
        self._streamer = Streamer(self).with_xyz(x, y, z)
        self._streamer.start()

    # ---------------------- 4. 위치 전송 ----------------------
    def send_setpoint(self, x, y, z):
        now_ms = int(time.time() * 1000) % 0xFFFFFFFF

        self._client.master.mav.set_position_target_local_ned_send(
            now_ms,
            self._client.master.target_system, self._client.master.target_component,
            self.MAV_FRAME_LOCAL_NED,
            0b0000111111111000,
            x, y, z, 0, 0, 0, 0, 0, 0, 0, 0
        )

