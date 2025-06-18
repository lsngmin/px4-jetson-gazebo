from common import Singleton
from constant import VtolStateEnum
from monitor import MonitorInterface

class VtolStateMonitor(MonitorInterface, Singleton):
    def __init__(self):
        super().__init__()

        self._on_condition_callback = None
        self.current_vtol_state = 0

    def _handle_message(self, msg):
        vtol_state = msg.vtol_state

        prev_v = self.current_vtol_state
        curr_v = vtol_state

        prev_n = VtolStateEnum(prev_v).name
        curr_n = VtolStateEnum(curr_v).name

        if prev_n != curr_n:
            self._logger.info(
                f"전환 이벤트 — {prev_n}({prev_v}) → {curr_n}({curr_v}) (비행 모드 변경 감지됨)")

        if curr_v == 3:
            if callable(self._on_condition_callback):
                self._on_condition_callback(True)

        else:
            if callable(self._on_condition_callback):
                self._on_condition_callback(False)

        self.current_vtol_state = vtol_state

    def set_trigger_callback(self, callback):
        self._on_condition_callback = callback

    def _get_monitor_config(self):
        return (
            'EXTENDED_SYS_STATE',
            f'모드 전환 감시 활성화 — 상태 변화를 대기 중입니다. (초기 vtol_state:{self.current_vtol_state})'
        )
