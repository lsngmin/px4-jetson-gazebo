import logging, time, platform

from config import configure_logging
from manager import DetectManager, FlightManager

def main():
    ########################################################################
    configure_logging(level=logging.DEBUG, log_dir = "./log", filename = "AppLog")
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
    FlightManager.get_instance()
    DetectManager.get_instance()
    # vtol_monitor = VtolStateMonitor()
    # wp_monitor = WaypointMonitor()
    # md_monitor = ModeMonitor.get_instance()
    # ls_monitor = LandedStateMonitor.get_instance()
    # ps_monitor = PositionMonitor.get_instance()
    #monitors = [vtol_monitor, wp_monitor, md_monitor, ls_monitor]

    # monitors = [vtol_monitor, wp_monitor]
    # AuthorityControl.get_instance().push_monitor(monitors)
    #monitors.append(ps_monitor)
    # for monitor in monitors:
    #     monitor.start()
    #
    # fc = FlightManager()
    # fc.set_target(z=-30.0)
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
