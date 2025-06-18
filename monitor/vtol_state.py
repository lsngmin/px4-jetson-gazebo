from common.singleton_mixin import SingletonMixin
from constant.vtol_state_enum import VtolStateEnum
from monitor.interface.monitor_interface import MonitorInterface

class VtolStateMonitor(MonitorInterface, SingletonMixin):
    def __init__(self):
        super().__init__()
        SingletonMixin.__init__(self)
        self._on_condition_callback = None

        # 비행체의 vtol_state value 를 저장. 초기에는 0으로 설정
        self.current_vtol_state = 0

    def set_trigger_callback(self, callback):
        self._on_condition_callback = callback

    def _get_monitor_config(self):
        return (
            'EXTENDED_SYS_STATE',
            f'모드 전환 감시 활성화 — 상태 변화를 대기 중입니다. (초기 vtol_state:{self.current_vtol_state})'
        )

    def _handle_message(self, msg):
        vtol_state = msg.vtol_state

        prev_v = self.current_vtol_state
        curr_v = vtol_state
        prev_n = VtolStateEnum(prev_v).name # 기존 vtol_state value
        curr_n = VtolStateEnum(curr_v).name # 받아온 vtol_state value

        if prev_n != curr_n:
            self._logger.info(
                f"전환 이벤트 — {prev_n}({prev_v}) → {curr_n}({curr_v}) (비행 모드 변경 감지됨)")
        if curr_v == 3: #todo int형으로 하는게 더 좋아보임
            if callable(self._on_condition_callback):
                self._on_condition_callback(True)  # True: 조건 만족!
        else:
            if callable(self._on_condition_callback):
                self._on_condition_callback(False)

        self.current_vtol_state = vtol_state
