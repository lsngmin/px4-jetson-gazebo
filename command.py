import logging
from pymavlink import mavutil

from core import MavLinkClient

class Command:
    cmd = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM

    def __init__(self):
        self._client = MavLinkClient.get_instance()
        self._config = self._client.config
        self._logger = logging.getLogger(self.__class__.__name__)
        self._c = self._client.master.mav

        self._ts = self._client.target_system # 시스템 ID
        self._tc = self._client.target_component # 컴포넌트 ID

    def arm(self):
        cmd = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM

        self._c.command_long_send(
            self._ts,
            self._tc,
            cmd,
            0, 1, 0, 0, 0, 0, 0, 0
        )

