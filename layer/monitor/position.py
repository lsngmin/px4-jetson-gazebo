from typing_extensions import override

from default import POSITION_CHANGED

from layer.monitor import Monitor
from common.pattern import Singleton
from common.util import PositionData

class PositionMonitor(Monitor, Singleton):
    def __init__(self):
        super().__init__("LOCAL_POSITION_NED")
        self._on_condition_callback = None
        self.current_position = None
        self._logger.info("위 경 고도 실시간 수신 시작")

    @override
    def _handle_message(self, msg):
        self._ed.publish(POSITION_CHANGED, PositionData.make(msg))