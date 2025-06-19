import threading, time, logging, yaml, os

from collections import defaultdict
from pymavlink import mavutil
from pydantic import BaseModel
from typing import Optional

from common import Singleton

class MavLinkClient(Singleton):
    def __init__(self):
        if self.__class__._initialized:
            return
        self.__class__._initialized = True

        self._logger = logging.getLogger(self.__class__.__name__)
        self.config = Config.from_yaml("application.yaml")
        self.master = mavutil.mavlink_connection(self.config.connection_uri)
        self._event_bus = EventDispatcher()

        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        while True:
            msg = self.master.recv_match(blocking=True, timeout=1)
            if msg:
                self._event_bus.publish(msg)
            else:
                time.sleep(0.1)

    def subscribe(self, msg_type, callback):
        self._event_bus.subscribe(msg_type, callback)

class EventDispatcher:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, msg_type, callback):
        self._subscribers[msg_type].append(callback)

    def publish(self, msg):
        for cb in self._subscribers[msg.get_type()]:
            cb(msg)

class Config(BaseModel):
    connection_uri: str
    rescue_target_lat: float
    rescue_target_lon: float
    rescue_target_tolerance: float
    debug_mode: Optional[bool] = False

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
