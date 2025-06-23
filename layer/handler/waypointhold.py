import threading

from pymavlink import mavutil

from default import POSITION_CHANGED, MODE_CHANGED, MODE_OFFBOARD_IN, MODE_OFFBOARD_OUT, VTOL_STATE_CHANGED, \
    RESCUE_POSITION_HIT, SET_MODE_OFFBOARD
from common.util import PositionData
from common.pattern import Singleton

from layer.handler.base import Handler

class WaypointHoldHandler(Handler, Singleton):
    def __init__(self):
        super().__init__()
        self._init_ed()
        self.current = {'x': 0.0, 'y': 0.0, 'z': 0.0}

        self._is_authority_active = False
        self._is_vtol_mc = False
        self._is_loiter_mode = False
        self._is_rescue_reached = False

        self._lock = threading.Lock()
        self._streamer = None

    def _init_ed(self):
        self._ed.subscribe(POSITION_CHANGED, self.on_position_changed)
        self._ed.subscribe(MODE_CHANGED, self.on_mode_changed)
        self._ed.subscribe(VTOL_STATE_CHANGED, self.on_vtol_mc_changed)
        self._ed.subscribe(RESCUE_POSITION_HIT, self.on_rescue_reached)

    def _on_authority_activated(self):
        checked = self._is_vtol_mc and self._is_loiter_mode and self._is_rescue_reached
        if checked and not self._is_authority_active:
            self._toc.publish(SET_MODE_OFFBOARD, self)
            # c.hold_position_takeoff(self.current['x'], self.current['y'], -30)
            self._logger.info("OFFBOARD 모드로 전환 완료. setpoint 스트림 유지 중!")
            self._is_authority_active = checked

    def on_vtol_mc_changed(self, is_mc: bool):
        self._is_vtol_mc = is_mc
        self._on_authority_activated()

    def on_mode_changed(self,  is_loiter: bool):
        self._is_loiter_mode = is_loiter
        self._on_authority_activated()

    def on_rescue_reached(self, is_reached: bool):
        self._is_rescue_reached = is_reached
        self._on_authority_activated()

    def on_position_changed(self, position: PositionData):
        self.current['x'] = position.x
        self.current['y'] = position.y
        self.current['z'] = position.z