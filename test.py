import logging, time

from common.logging import configure_logging
from layer.handler import WaypointHoldHandler
from layer.monitor import ModeMonitor, VtolStateMonitor, PositionMonitor,RescuePositionMonitor
from layer.command import Command
if __name__ == "__main__":
    configure_logging(level=logging.DEBUG, log_dir = "./log", filename = "AppLog")
    c = Command()
    time.sleep(2)

    ModeMonitor.get_instance()
    VtolStateMonitor.get_instance()
    PositionMonitor.get_instance()
    RescuePositionMonitor.get_instance()
    WaypointHoldHandler.get_instance()



    # DetectManager.get_instance()
    while True:
        time.sleep(1)



