from typing_extensions import override

from common.singleton import Singleton
from constant import decode_px4_mode
from monitor.interface.monitor_interface import MonitorInterface

class ModeMonitor(MonitorInterface, Singleton):
    def __init__(self):
        super().__init__()

        self._on_condition_callback = None
        self._current_mode = None

    @override
    def _handle_message(self, msg):
        """
        PX4 HEARTBEAT 메시지에서 비행 모드를 추출해
        내부 상태를 갱신하고, 변화 시 로그를 남김.
        """
        # mode 추출 (PX4/MAVLink의 base_mode/custom_mode 프로토콜)
        mode = decode_px4_mode(msg.custom_mode)
        if mode == "AUTO:LOITER":
            self._on_condition_callback(True)
        else:
            self._on_condition_callback(False)

        if mode != self._current_mode:
            self._logger.info(f"PX4 모드 변경 감지 — {self._current_mode} → {mode}")
            self._current_mode = mode

    @override
    def _register_callback(self, callback):
        self._on_condition_callback = callback

    def _get_monitor_config(self):
        return (
            'HEARTBEAT',
            "PX4 비행 모드 감시 활성화 — 상태 변화를 대기 중입니다."
        )
