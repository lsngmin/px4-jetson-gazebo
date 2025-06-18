import logging
import time
from control.authority import AuthorityControl
from control.interface.control import ControlInterface
from logging_config import configure_logging
import platform

from mavlink.mavlinkClient import PymavlinkClient
from monitor.landed_state import LandedStateMonitor
from monitor.mode import ModeMonitor
from monitor.interface.monitor_interface import MonitorInterface
from monitor.position import PositionMonitor
from monitor.vtol_state import VtolStateMonitor
from monitor.waypoint import WaypointMonitor
from config import Config


def main():
    configure_logging(level=logging.INFO, log_dir = "./log", filename = "AppLog")
    py_ver = platform.python_version()
    Config.from_yaml("application.yaml")



    logger = logging.getLogger(__name__)
    logger.info(f"""
              ___  Start AutoControl System !
           __/___\__ acs_version_1.0.0
          /  o   o  \\ 2025.06.13
         |           | Running Environmnet is 'sim'
          \____v____/ System ROS Distro is 'Humble' :)
             /   \\ Your System Python Version is '{py_ver}'
        """
                )

    MonitorInterface.set_mav_client(PymavlinkClient.get_instance())
    MonitorInterface.set_config(Config.get_instance())

    ControlInterface.set_mav_client(PymavlinkClient.get_instance())
    ControlInterface.set_config(Config.get_instance())

    vtol_monitor = VtolStateMonitor.get_instance()
    wp_monitor = WaypointMonitor.get_instance()
    md_monitor = ModeMonitor.get_instance()
    ls_monitor = LandedStateMonitor.get_instance()
    ps_monitor = PositionMonitor.get_instance()

    monitors = [vtol_monitor, wp_monitor, md_monitor, ls_monitor]
    AuthorityControl.get_instance().push_monitor(monitors)
    monitors.append(ps_monitor)
    for monitor in monitors:
        monitor.start()

    while True:
        time.sleep(1)
if __name__ == "__main__":
    main()
