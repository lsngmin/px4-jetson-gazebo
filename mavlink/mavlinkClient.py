from pymavlink import mavutil
import threading

from common.singleton_mixin import SingletonMixin
from mavlink.event_dispatcher import EventDispatcher


class PymavlinkClient(SingletonMixin):
    def __init__(self, connection_string="udp:127.0.0.1:14560", event_bus=None):
        SingletonMixin.__init__(self)
        self.master = mavutil.mavlink_connection(connection_string)
        self._event_bus = event_bus or EventDispatcher()
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        while True:
            msg = self.master.recv_match(blocking=True, timeout=1)
            if msg:
                self._event_bus.publish(msg)

    def subscribe(self, msg_type, callback):
        self._event_bus.subscribe(msg_type, callback)

# class PymavlinkClient(MavlinkClientInterface):
#     def __init__(self, connection_string="udp:127.0.0.1:14540"):
#         # 드론의 펌웨어랑 mavlink로 통신을 연결. connection_string은 변경하지 않는다.
#         self.master = mavutil.mavlink_connection(connection_string)
#         # vtol 상태가 바뀔 때 실행할 함수 목록을 저장할 리스트.
#         self._vtol_callbacks = []
#
#         self._handlers = {
#             'EXTENDED_SYS_STATE': self._handle_vtol_state
#             # 'GLOBAL_POSITION_INT': self._handle_position,
#             # ...
#         }
#         # _listen 함수를 별도의 쓰레드에서 무한 실행.
#         # 메인 프로그램이 멈추지 않고, 백그라운드에서 계속 mavlink 메시지를 받아 vtol 상태를 감지
#         threading.Thread(target=self._listen, daemon=True).start()
#
#     def _listen(self):
#         while True:
#             # 무한 루프로 계속 PX4로부터 EXTENDED_SYS_STATE 메시지만 감시.
#             msg = self.master.recv_match(blocking=True, timeout=1)
#             # 새 메시지가 오면 vtol_state 값을 꺼냄
#             if msg:
#                 handler = self._handlers.get(msg.get_type())
#                 if handler:
#                     handler(msg)
#
#     def subscribe_vtol_state(self, callback: Callable[[int], None]) -> None:
#         self._vtol_callbacks.append(callback)
#
#     def _handle_vtol_state(self, msg):
#         vtol_state = msg.vtol_state
#         for cb in self._vtol_callbacks:
#             cb(vtol_state)
#
#     def _handle_position(self, msg):
#         return
#         # self._pos_callbacks.append(callback)