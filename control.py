from abc import ABC, abstractmethod
import logging

from common import Singleton
from core import MavLinkClient
from manager.base.base_manager import BaseManager
from monitor import VtolStateMonitor, ModeMonitor, RescuePositionMonitor



class ControlInterface(ABC):
    def __init__(self):
        self._client = MavLinkClient.get_instance()
        self._config = self._client.config
        self._logger = logging.getLogger(self.__class__.__name__)

    def start_with_callback(self, callback):
        self._register_callback(callback)
        return self

    @abstractmethod
    def _register_callback(self, callback):
        pass

class AuthorityControl(ControlInterface, Singleton):
    def __init__(self):
        super().__init__()

        self._vtol_state_monitor = VtolStateMonitor.get_instance().start_with_callback(self.on_vtol_mc_changed)
        self._mode_monitor = ModeMonitor.get_instance().start_with_callback(self.on_mode_changed)
        self._rescue_position_monitor = RescuePositionMonitor.get_instance().start_with_callback(self.on_rescue_reached)

        self._is_vtol_mc = False
        self._is_loiter_mode = False
        self._is_rescue_reached = False
        self._condition_met  = False
        self._on_condition_callback = None

    def on_vtol_mc_changed(self, is_mc: bool):
        self._is_vtol_mc = is_mc
        self._check_and_trigger()

    def on_mode_changed(self,  is_loiter: bool):
        self._is_loiter_mode = is_loiter
        self._check_and_trigger()

    def on_rescue_reached(self, is_reached: bool):
        self._is_rescue_reached = is_reached
        self._check_and_trigger()

    def _check_and_trigger(self):
        checked = self._is_vtol_mc and self._is_loiter_mode and self._is_rescue_reached
        if callable(self._on_condition_callback):
            self._on_condition_callback(checked)

    def _register_callback(self, callback):
        self._on_condition_callback = callback

class DetectManager(BaseManager,Singleton):
    CONF_THRESH = 0.6
    FPS_LIMIT = 15.0

    def __init__(self):
        super(DetectManager, self).__init__()

        #---------------------- 외부 인스턴스 초기화----------------------#
        ## _client, _config -> MAVLink 클라이언트 인스턴스 및 설정
        ## _logger -> 로거 초기화
        ## _detector -> 카메라 및 모델 초기화
        ## ed.subscribe -> "hold_ready" 이벤트 수신 시 _on_hold_ready 호출
        #----------------------                ----------------------#
        self._client = MavLinkClient.get_instance()
        self._config = self._client.config
        self._logger = logging.getLogger(self.__class__.__name__)
        self._detector = Detector()
        self.ed.subscribe("hold_ready", self._on_hold_ready)

        #----------------------내부 인스턴스 초기화----------------------#
        self._thread = None
        self._stop_evt = threading.Event()

    def _on_hold_ready(self, _=None):
        if self._thread and self._thread.is_alive():
            return
        self._stop_evt.clear()
        self._thread = threading.Thread(target=self._detect_loop,
                                        name="DetectLoop", daemon=True)
        self._thread.start()
        #TODO: 카메라와 모델의 초기작업은 프로그램 실행시 되었다는 가정
        #TODO: 이미 카메라와 모델은 연결되어 있다는 가정
        #TODO: 그냥 객체 인식 시작하는 프로세스 추가
        #TODO: 해당 클래스에서는 객체 인식 결과 값을 받아 신뢰도와 클래스별 분류 하는 과정
        #TODO: 그리고 거리 계산 함수를 사용해 착륙 매니저에게 착륙 위치와 함꼐 publish
    def _detect_loop(self):
        while not self._stop_evt.is_set():
            result = self._detector.infer()
            if result is None:
                time.sleep(1.0 / self.FPS_LIMIT)
                continue
            # "조난자" 라벨 및 신뢰도 검사
            if result.label == "조난자" and result.confidence >= self.CONF_THRESH:
                # TODO: px→NED 거리 계산 (pixel_to_ned 등 사용)
                # dx, dy = pixel_to_ned(...)
                # landing_point 구성 예시
                # landing_point = {"x": dx, "y": dy, "z": 0.0}
                landing_point = {"x": 0, "y": 0, "z": 0.0}
                # self._logger.info(
                #     "Target found: dx=%.2f dy=%.2f conf=%.2f",
                #     dx, dy, result.confidence
                # )
                # 착륙 매니저로 이벤트 발행

                self.ed.publish("landing_target", landing_point)
                break

            time.sleep(1.0 / self.FPS_LIMIT)

    def stop_detection(self):
        self._stop_evt.set()
        if self._thread:
            self._thread.join(timeout=1.0)

