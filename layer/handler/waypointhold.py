import threading
from collections import namedtuple

from pymavlink import mavutil

from default import POSITION_CHANGED, MODE_CHANGED, VTOL_STATE_CHANGED, \
    RESCUE_POSITION_HIT, SET_MODE_OFFBOARD, HOLD_ALTITUDE, AutoSubMode
from common.util import PositionData
from common.pattern import Singleton

from layer.handler.base import Handler

class WaypointHoldHandler(Handler, Singleton):
    def __init__(self):
        super().__init__()

    def _on_authority_activated(self):
        checked = self._is_vtol_mc and self._current_mode is AutoSubMode.LOITER and self._is_rescue_reached
        if checked and not self._is_authority_active:
            self._toc.publish(SET_MODE_OFFBOARD, self)
            self._logger.info("OFFBOARD 모드로 전환 완료. setpoint 스트림 유지 중!")
            Position = namedtuple("Position", ["x", "y", "z"])
            pos = Position(self.current["x"], self.current["y"], -30)

            self._toc.publish(HOLD_ALTITUDE, pos)
            self._is_authority_active = checked