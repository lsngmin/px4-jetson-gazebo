from typing_extensions import override

from default import MODE_CHANGED, decode_px4_mode
from common.pattern import Singleton
from layer.monitor import Monitor

class ModeMonitor(Monitor, Singleton):
    def __init__(self):
        super().__init__('HEARTBEAT')
        self._current_mode = None

        self._logger.info("PX4 비행 모드 감시 활성화 — 상태 변화를 대기 중입니다.")

    @override
    def _handle_message(self, msg):
        """
        PX4 HEARTBEAT 메시지에서 비행 모드를 추출해
        내부 상태를 갱신하고, 변화 시 로그를 남김.
        """
        # mode 추출 (PX4/MAVLink의 base_mode/custom_mode 프로토콜)
        mode = decode_px4_mode(msg.custom_mode)
        if mode == "AUTO:LOITER":
            self._ed.publish(MODE_CHANGED, True)
        else:
            self._ed.publish(MODE_CHANGED, False)

        if mode != self._current_mode:
            self._logger.info(f"PX4 모드 변경 감지 — {self._current_mode} → {mode}")
            self._current_mode = mode