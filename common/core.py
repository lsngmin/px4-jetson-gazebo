import threading, time, logging

from pymavlink import mavutil

from common import Config, Singleton, EventDispatcher

class MavLinkClient(Singleton):
    def __init__(self):
        if self.__class__._initialized:
            return
        self.__class__._initialized = True

        self._logger = logging.getLogger(self.__class__.__name__)
        self.config = Config.from_yaml("./application.yaml")
        self.master = mavutil.mavlink_connection(self.config.connection_uri)
        self._event_bus = EventDispatcher()

        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        while True:
            msg = self.master.recv_match(blocking=True, timeout=1)
            if msg and msg.get_type() == 'HEARTBEAT':
                print(msg)
            if msg:
                self._event_bus.publish(msg)
            else:
                time.sleep(0.1)

    def subscribe(self, msg_type, callback):
        self._event_bus.subscribe(msg_type, callback)
