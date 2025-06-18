from pydantic import BaseModel, Field

from common import Singleton
from monitor import MonitorInterface

class PositionData(BaseModel):
    lat: float = Field(..., description="위도 (도)")
    lon: float = Field(..., description="경도 (도)")
    alt: float = Field(..., description="상대 고도 (m)")
    rel_alt: float = Field(..., description="지면 기준 상대 고도 (m)")
    heading: float = Field(..., description="기체 방향 (도)")

    @classmethod
    def from_msg(cls, msg):
        return cls(
            lat=msg.lat / 1e7,
            lon=msg.lon / 1e7,
            alt=msg.alt / 1000,
            rel_alt=msg.relative_alt / 1000,
            heading=(msg.hdg / 100.0) if msg.hdg != 65535 else -1.0
        )

class PositionMonitor(MonitorInterface, Singleton):
    def __init__(self):
        super().__init__()

        self._on_update_callback = None
        self.current_position = None  # type: Optional[PositionData]

    def _handle_message(self, msg):
        self.current_position = PositionData.from_msg(msg)
        if callable(self._on_update_callback):
            self._on_update_callback(self.current_position)

    def set_trigger_callback(self, callback):
        self._on_update_callback = callback

    def _get_monitor_config(self):
        return (
            "GLOBAL_POSITION_INT",
            "위 경 고도 실시간 수신 시작"
        )