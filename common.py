import threading, time
from collections import defaultdict
from typing import Callable, Any


class EventDispatcher:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, msg_type, callback):
        self._subscribers[msg_type].append(callback)

    def publish(self, msg):
        for cb in self._subscribers[msg.get_type()]:
            cb(msg)

class MEventDispatcher:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_name: str, callback: Callable[[Any], None]):
        self._subscribers[event_name].append(callback)

    def publish(self, event_name: str, payload: Any = None):
        for cb in self._subscribers.get(event_name, []):
            cb(payload)


class Singleton:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return cls(*args, **kwargs)

class Streamer(threading.Thread):
    def __init__(self, manager, sleep=0.02):
        super().__init__(daemon=True)
        self.manager = manager
        self.sleep = sleep
        self._stop_event = threading.Event()

    def run(self):
        self.manager._logger.info("Setpoint 스트리밍 시작")
        count = 0
        while not self._stop_event.is_set():
            try:
                x, y, z = self.manager.get_setpoint()
                self.manager.send_setpoint(x, y, z)
                count += 1
                if count % 50 == 0:  # 1초마다 로그
                    self.manager._logger.debug(f"Setpoint 전송 중: {count}회")
                time.sleep(self.sleep)
            except Exception as e:
                self.manager._logger.error(f"Setpoint 전송 오류: {e}")
                time.sleep(self.sleep)
        self.manager._logger.info("Setpoint 스트리밍 종료")

    def stop(self):
        self._stop_event.set()