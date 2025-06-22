import logging

from pydantic import BaseModel, Field
from typing_extensions import override
from abc import ABC, abstractmethod

from core import MavLinkClient
from common import Singleton
from constant import VtolStateEnum, decode_px4_mode
from util import Location

class MonitorInterface(ABC):
    def __init__(self):
        self._client = MavLinkClient.get_instance()
        self._config = self._client.config
        self._logger = logging.getLogger(self.__class__.__name__)

    def start_with_callback(self, callback):
        msg_type, log_msg = self._get_monitor_config()
        self._client.subscribe(msg_type, self._handle_message)
        self._logger.info(log_msg)
        self._register_callback(callback)
        return self

    @abstractmethod
    def _get_monitor_config(self):
        """
        return (
            'msg_type',
            'log_msg'
        )
        """
        pass

    @abstractmethod
    def _handle_message(self, msg):
        pass

    @abstractmethod
    def _register_callback(self, callback):
        pass

class VtolStateMonitor(MonitorInterface, Singleton):
    def __init__(self):
        super().__init__()
        self._on_condition_callback = None
        self.current_vtol_state     = 0

    @override
    def _handle_message(self, msg):
        vtol_state = msg.vtol_state

        prev_v = self.current_vtol_state
        curr_v = vtol_state

        prev_n = VtolStateEnum(prev_v).name
        curr_n = VtolStateEnum(curr_v).name

        if prev_n != curr_n:
            self._logger.info(
                f"전환 이벤트 — {prev_n}({prev_v}) → {curr_n}({curr_v}) (비행 모드 변경 감지됨)")

        if curr_v == 3:
            if callable(self._on_condition_callback):
                self._on_condition_callback(True)

        else:
            if callable(self._on_condition_callback):
                self._on_condition_callback(False)

        self.current_vtol_state = vtol_state

    @override
    def _register_callback(self, callback):
        self._on_condition_callback = callback

    @override
    def _get_monitor_config(self):
        return (
            'EXTENDED_SYS_STATE',
            f'모드 전환 감시 활성화 — 상태 변화를 대기 중입니다. (초기 vtol_state:{self.current_vtol_state})'
        )
class WaypointMonitor(MonitorInterface, Singleton):
    def _register_callback(self, callback):
        pass

    def __init__(self):
        super().__init__()

        self._on_condition_callback = None
        # 초기화 할 때 조난자 위치의 좌표를 입력 초기화 해야 목표 위치가 업데이트.
        self._target_location = Location(
            self._config.rescue_target.latitude,
            self._config.rescue_target.longitude
        )
        self.radius_m = self._config.rescue_target.radius
        self.hold_count = self._config.rescue_target.hold_count

        self._counter = 0
        self._inside = False

    def set_trigger_callback(self, callback):
        self._on_condition_callback = callback

    def _handle_message(self, msg):
        current = Location(msg.lat, msg.lon)
        distance = current.distance_to(self._target_location)
        was_inside = self._inside


        if distance <= self.radius_m:
            self._counter += 1
            if self._counter >= self.hold_count:
                self._inside = True
        else:
            self._counter = 0
            self._inside = False

        if was_inside != self._inside:
            # status = "목표 반경 진입" if self._inside else "목표 반경 이탈"
            self._logger.info(
                "[WaypointMonitor] {status}: 반경 {self.radius_m}m, "
                "연속 {self.hold_count}회, 거리 {distance:.2f}m"
            )
            # 콜백 호출 (진입/이탈 모두 반영)
            if self._on_condition_callback:
                self._on_condition_callback(self._inside)

    def _get_monitor_config(self):
        return (
            'GLOBAL_POSITION_INT',
            f"위치 모니터 시작 — 목표:({self._target_location.lat},{self._target_location.lon}), 반경:{self.radius_m}m"
        )

class RescuePositionMonitor(MonitorInterface, Singleton):
    def __init__(self):
        super().__init__()
        self._target_lat = self._config.rescue_target_lat
        self._target_lon = self._config.rescue_target_lon
        self._target_tolerance = self._config.rescue_target_tolerance
        self._on_condition_callback = None
        self._is_rescue_reached = None

    #TODO: GPS 좌표가 어떻게 들어올 지, 어떤 형식으로 들어올 지 아직 모름.
    #TODO: 나중에 확정되면 로직 변경 필요할거 같음
    @override
    def _handle_message(self, msg):
        current_location = Location(lat=msg.lat/1e7, lon=msg.lon/1e7)
        target_location = Location(lat=self._target_lat, lon=self._target_lon)

        distance = current_location.distance_to(target_location)
        reached = distance < self._target_tolerance
        if reached and not self._is_rescue_reached:
            self._logger.info(f"조난자 위치에 도달했습니다. - 반경 {distance:.1f}m")
        elif not reached and self._is_rescue_reached:
            self._logger.info(f"조난자 위치에서 이탈했습니다. - 반경 {distance:.1f}m")

        self._is_rescue_reached = reached

        if callable(self._on_condition_callback):
            self._on_condition_callback(reached)

    @override
    def _register_callback(self, callback):
        self._on_condition_callback = callback

    @override
    def _get_monitor_config(self):
        return (
            'GLOBAL_POSITION_INT',
            f'조난자 위치 도달 감시 활성화 — 목표 위치: ({self._target_lat}, {self._target_lon})'
        )

class PositionData(BaseModel):
    x: float = Field(..., description="현재 x (미터, 북쪽 기준)")
    y: float = Field(..., description="현재 y (미터, 동쪽 기준)")
    z: float = Field(..., description="현재 z (미터, 아래로 증가)")

    @classmethod
    def make(cls, msg):
        return cls(
            x = msg.x,
            y = msg.y,
            z = msg.z
        )

class PositionMonitor(MonitorInterface, Singleton):
    def __init__(self):
        super().__init__()
        self._on_condition_callback = None
        self.current_position = None

    @override
    def _handle_message(self, msg):
        self.current_position = PositionData.make(msg)
        if callable(self._on_condition_callback):
            self._on_condition_callback(self.current_position)

    @override
    def _register_callback(self, callback):
        self._on_condition_callback = callback

    @override
    def _get_monitor_config(self):
        return (
            "LOCAL_POSITION_NED",
            "위 경 고도 실시간 수신 시작"
        )
class ModeMonitor(MonitorInterface, Singleton):
    def __init__(self):
        super().__init__()

        self._on_condition_callback = None
        self._current_mode = None

    @override
    def _handle_message(self, msg):
        """
        PX4 HEARTBEAT 메시지에서 비행 모드를 추출해
        내부 상태를 갱신하고, 변화 시 로그를 남김.
        """
        # mode 추출 (PX4/MAVLink의 base_mode/custom_mode 프로토콜)
        mode = decode_px4_mode(msg.custom_mode)
        if mode == "AUTO:LOITER":
            self._on_condition_callback(True)
        else:
            self._on_condition_callback(False)

        if mode != self._current_mode:
            self._logger.info(f"PX4 모드 변경 감지 — {self._current_mode} → {mode}")
            self._current_mode = mode

    @override
    def _register_callback(self, callback):
        self._on_condition_callback = callback

    def _get_monitor_config(self):
        return (
            'HEARTBEAT',
            "PX4 비행 모드 감시 활성화 — 상태 변화를 대기 중입니다."
        )
# class LandedStateMonitor(MonitorInterface, Singleton):
#     def __init__(self):
#         super().__init__()
#
#         self._current_state = LandedStateEnum.UNDEFINED
#         self._on_condition_callback = None  # type: callable[[LandedStateEnum], None]
#
#     # ----- 외부 API ---------------------------------------------------------
#
#     def set_trigger_callback(self, cb):
#         """상태가 바뀔 때 호출할 콜백 등록. 인자 = LandedStateEnum."""
#         self._on_condition_callback = cb
#
#     # ----- MonitorInterface 구현 -------------------------------------------
#
#     def _get_monitor_config(self):
#         return (
#             "EXTENDED_SYS_STATE",
#             f"이륙/착륙 상태 감시 시작… (초기값 {self._current_state.name})"
#         )
#
#     def _handle_message(self, msg):
#         new_state = LandedStateEnum(msg.landed_state)
#
#         if new_state != self._current_state:
#             self._logger.info(
#                 f"[LANDED] {self._current_state.name} → {new_state.name} ({new_state.value})"
#             )
#             self._current_state = new_state
#
#             # 콜백이 등록돼 있으면 알림
#             if callable(self._on_condition_callback):
#                 self._on_condition_callback(new_state)