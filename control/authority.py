from common import Singleton
from control import ControlInterface
from monitor import VtolStateMonitor, ModeMonitor, RescuePositionMonitor

class AuthorityControl(ControlInterface, Singleton):
    def __init__(self):
        super().__init__()

        self._vtol_state_monitor = VtolStateMonitor.get_instance().start_with_callback(self.on_vtol_mc_changed)
        self._mode_monitor = ModeMonitor.get_instance().start_with_callback(self.on_mode_changed)
        self._rescue_position_monitor = RescuePositionMonitor.get_instance().start_with_callback(self.on_rescue_reached)

        self._is_vtol_mc = False
        self._is_loiter_mode = False
        self._is_rescue_reached = False
        self._condition_met  = False
        self._on_condition_callback = None

    def on_vtol_mc_changed(self, is_mc: bool):
        self._is_vtol_mc = is_mc
        self._check_and_trigger()

    def on_mode_changed(self,  is_loiter: bool):
        self._is_loiter_mode = is_loiter
        self._check_and_trigger()

    def on_rescue_reached(self, is_reached: bool):
        self._is_rescue_reached = is_reached
        self._check_and_trigger()

    def _check_and_trigger(self):
        checked = self._is_vtol_mc and self._is_loiter_mode and self._is_rescue_reached
        if callable(self._on_condition_callback):
            self._on_condition_callback(checked)

    def _register_callback(self, callback):
        self._on_condition_callback = callback
