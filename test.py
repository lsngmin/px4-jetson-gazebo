import logging, time

from common.logging import configure_logging

from layer.handler import WaypointHoldHandler
from layer.handler.detectstart import DetectStartHandler
from layer.monitor import ModeMonitor, VtolStateMonitor, PositionMonitor,RescuePositionMonitor
from layer.command import Command

if __name__ == "__main__":
    configure_logging(level=logging.DEBUG, log_dir = "./log", filename = "AppLog")
    #----------------------  Command 계층  ----------------------
    c = Command.get_instance()

    #----------------------  Monitor 계층  ----------------------
    ModeMonitor.get_instance()
    VtolStateMonitor.get_instance()
    PositionMonitor.get_instance()
    RescuePositionMonitor.get_instance()

    #----------------------  Handler 계층  ----------------------
    WaypointHoldHandler.get_instance()
    DetectStartHandler.get_instance()
    time.sleep(10)

    c.arm()

    while True:
        time.sleep(1)



