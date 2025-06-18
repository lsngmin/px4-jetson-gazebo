from collections import defaultdict

class EventDispatcher:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, msg_type, callback):
        self._subscribers[msg_type].append(callback)

    def publish(self, msg):
        for cb in self._subscribers[msg.get_type()]:
            cb(msg)
