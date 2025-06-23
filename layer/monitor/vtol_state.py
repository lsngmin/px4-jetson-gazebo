from typing_extensions import override

from default import VTOL_STATE_CHANGED, VtolStateEnum

from layer.monitor import Monitor
from common.pattern import Singleton

class VtolStateMonitor(Monitor, Singleton):
    def __init__(self):
        super().__init__('EXTENDED_SYS_STATE')
        self.current_vtol_state     = 0

        self._logger.info(f'모드 전환 감시 활성화 — 상태 변화를 대기 중입니다. (초기 vtol_state:{self.current_vtol_state}')

    @override
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
            self._ed.publish(VTOL_STATE_CHANGED, True)
        else:
            self._ed.publish(VTOL_STATE_CHANGED, False)

        self.current_vtol_state = vtol_state