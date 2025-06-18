from common.singleton_mixin import SingletonMixin
from constant.landed_state_enum import LandedStateEnum
from monitor.interface.monitor_interface import MonitorInterface

class LandedStateMonitor(MonitorInterface, SingletonMixin):
    def __init__(self):
        super().__init__()
        SingletonMixin.__init__(self)

        self._current_state = LandedStateEnum.UNDEFINED
        self._on_condition_callback = None  # type: callable[[LandedStateEnum], None]

    # ----- 외부 API ---------------------------------------------------------

    def set_trigger_callback(self, cb):
        """상태가 바뀔 때 호출할 콜백 등록. 인자 = LandedStateEnum."""
        self._on_condition_callback = cb

    # ----- MonitorInterface 구현 -------------------------------------------

    def _get_monitor_config(self):
        return (
            "EXTENDED_SYS_STATE",
            f"이륙/착륙 상태 감시 시작… (초기값 {self._current_state.name})"
        )

    def _handle_message(self, msg):
        new_state = LandedStateEnum(msg.landed_state)

        if new_state != self._current_state:
            self._logger.info(
                f"[LANDED] {self._current_state.name} → {new_state.name} ({new_state.value})"
            )
            self._current_state = new_state

            # 콜백이 등록돼 있으면 알림
            if callable(self._on_condition_callback):
                self._on_condition_callback(new_state)
