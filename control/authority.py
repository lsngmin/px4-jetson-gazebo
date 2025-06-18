from common.singleton_mixin import SingletonMixin
from constant.landed_state_enum import LandedStateEnum
from control.interface.control import ControlInterface
from monitor.mode import ModeMonitor
from monitor.vtol_state import VtolStateMonitor
from monitor.waypoint import WaypointMonitor

PX4_CUSTOM_MODE_OFFBOARD = 6

class AuthorityControl(ControlInterface, SingletonMixin):
    def _get_monitor_config(self):
        return ("", "")

    def __init__(self):
        super().__init__()
        SingletonMixin.__init__(self)
        self._monitors = []
        self._vtol_status = False
        self._waypoint_status = False
        self._mode_offboard = False

        self._triggered = False

    def push_monitor(self, monitors):
        self._monitors = monitors
        self._register_callbacks()
        return self

    def _register_callbacks(self):
        for monitor in self._monitors:
            if isinstance(monitor, VtolStateMonitor):
                monitor.set_trigger_callback(self.on_vtol_state_changed)
            elif isinstance(monitor, WaypointMonitor):
                monitor.set_trigger_callback(self.on_waypoint_arrived)
            elif isinstance(monitor, ModeMonitor):
                monitor.set_trigger_callback(self.is_mode_offboard)

    def on_vtol_state_changed(self, flag: bool):
        self._vtol_status = flag
        self._check_and_trigger()

    def on_waypoint_arrived(self, flag: bool):
        self._waypoint_status = flag
        self._check_and_trigger()

    def is_mode_offboard(self, flag: bool):
        self._mode_offboard = flag
        self._check_and_trigger()

    def on_landed_state_changed(state):
        if state is LandedStateEnum.ON_GROUND:
            print("🛑 완전히 착륙!")
        elif state is LandedStateEnum.TAKEOFF:
            print("🚀 이륙 단계 진입")

    def _check_and_trigger(self):
        # if all([self._waypoint_status, self._vtol_status]):
        if all([self._vtol_status, not self._mode_offboard]):
            self._triggered = True
            # self._mav_client.master.set_mode_apm(PX4_CUSTOM_MODE_OFFBOARD)