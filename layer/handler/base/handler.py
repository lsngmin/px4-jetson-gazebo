import logging
from typing import Union

from common import MEventDispatcher, M2EventDispatcher
from common.core import MavLinkClient
from default import POSITION_CHANGED, MODE_CHANGED, VTOL_STATE_CHANGED, \
    RESCUE_POSITION_HIT, SET_MODE_OFFBOARD, HOLD_ALTITUDE, MainMode, AutoSubMode, VISION_UV
from common.util import PositionData
from common.messages import UV
class Handler:
    def __init__(self) -> None:
        self._ed: MEventDispatcher = MEventDispatcher.instance()
        self._toc: M2EventDispatcher = M2EventDispatcher.instance()
        self._client: MavLinkClient = MavLinkClient.get_instance()
        self._config = self._client.config
        self._logger = logging.getLogger(self.__class__.__name__)

        self._is_authority_active = False
        self._is_vtol_mc = False
        self._current_mode = None
        self._is_rescue_reached = False
        self.current = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self._uv = None
        self._init_ed()

    def _init_ed(self):
        self._ed.subscribe(POSITION_CHANGED, self.on_position_changed)
        self._ed.subscribe(MODE_CHANGED, self.on_mode_changed)
        self._ed.subscribe(VTOL_STATE_CHANGED, self.on_vtol_mc_changed)
        self._ed.subscribe(RESCUE_POSITION_HIT, self.on_rescue_reached)
        self._ed.subscribe(VISION_UV, self.on_vision_uv_changed)

    def on_vision_uv_changed(self, uv: UV):
        self._uv = uv

    def on_vtol_mc_changed(self, is_mc: bool):
        self._is_vtol_mc = is_mc
        self._on_authority_activated()

    def on_mode_changed(self,  mode: Union[MainMode, AutoSubMode]):
        self._current_mode = mode
        self._on_authority_activated()

    def on_rescue_reached(self, is_reached: bool):
        self._is_rescue_reached = is_reached
        self._on_authority_activated()

    def on_position_changed(self, position: PositionData):
        self.current['x'] = position.x
        self.current['y'] = position.y
        self.current['z'] = position.z

    def _on_authority_activated(self):
        pass