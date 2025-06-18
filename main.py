import logging, time, platform

from common import configure_logging

from monitor.vtol_state import VtolStateMonitor
from monitor.waypoint import WaypointMonitor


def main():
    ########################################################################
    configure_logging(level=logging.INFO, log_dir = "./log", filename = "AppLog")
    py_ver = platform.python_version()
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
    ########################################################################

    vtol_monitor = VtolStateMonitor()
    wp_monitor = WaypointMonitor()
    # md_monitor = ModeMonitor.get_instance()
    # ls_monitor = LandedStateMonitor.get_instance()
    # ps_monitor = PositionMonitor.get_instance()
    #monitors = [vtol_monitor, wp_monitor, md_monitor, ls_monitor]

    monitors = [vtol_monitor, wp_monitor]
    # AuthorityControl.get_instance().push_monitor(monitors)
    #monitors.append(ps_monitor)
    for monitor in monitors:
        monitor.start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
