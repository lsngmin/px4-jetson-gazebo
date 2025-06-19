from pydantic import BaseModel, Field
from typing_extensions import override

from common import Singleton
from monitor import MonitorInterface

class PositionData(BaseModel):
    x: float = Field(..., description="현재 x (미터, 북쪽 기준)")
    y: float = Field(..., description="현재 y (미터, 동쪽 기준)")
    z: float = Field(..., description="현재 z (미터, 아래로 증가)")

    @classmethod
    def make(cls, msg):
        return cls(
            x = msg.x,
            y = msg.y,
            z = msg.z
        )

class PositionMonitor(MonitorInterface, Singleton):
    def __init__(self):
        super().__init__()
        self._on_condition_callback = None
        self.current_position = None

    @override
    def _handle_message(self, msg):
        self.current_position = PositionData.make(msg)
        if callable(self._on_condition_callback):
            self._on_condition_callback(self.current_position)

    @override
    def _register_callback(self, callback):
        self._on_condition_callback = callback

    @override
    def _get_monitor_config(self):
        return (
            "LOCAL_POSITION_NED",
            "위 경 고도 실시간 수신 시작"
        )