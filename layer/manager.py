# import time, logging, threading
#
# from pymavlink import mavutil
#
# from common.core import MavLinkClient
# from common import Singleton, MEventDispatcher
# from common.detect import Detector
#
# from layer import Command
# from layer.monitor import PositionMonitor, PositionData, VtolStateMonitor, ModeMonitor, RescuePositionMonitor
#
#
# class LandingManager(BaseManager, Singleton):
#     """
#     LandingManager는 DetectManager로부터 받은 landing_target 이벤트로
#     정밀 착륙(precision landing) 시퀀스를 수행합니다.
#
#     1. 수평 Approach
#     2. 단계별 하강
#     3. 최종 LAND 명령 전송
#     """
#     # 허용 오차 및 단계 설정
#     XY_TOL = 0.05          # 수평 오차 허용범위 (m)
#     DESCENT_STEP = 0.2     # 하강 단계 거리 (m)
#     STEP_DELAY = 0.5       # 각 단계별 대기 시간 (s)
#
#     def __init__(self):
#         super(LandingManager, self).__init__()
#
#         # ---------------------- 외부 인스턴스 초기화 ---------------------- #
#         # MAVLink 클라이언트 인스턴스 및 설정
#         self._client = MavLinkClient.get_instance()
#         self._config = self._client.config
#         # 로거 초기화
#         self._logger = logging.getLogger(self.__class__.__name__)
#         # 이벤트 수신: landing_target
#         self.ed.subscribe("landing_target", self._on_landing_target)
#         # ---------------------------------------------------------------- #
#
#     def _on_landing_target(self, landing_point: dict):
#         """
#         landing_point: { 'x': float, 'y': float, 'z': float }
#         dx, dy, dz는 NED 오프셋(상대 위치) 또는 절대 목표 좌표로 가정.
#         """
#         dx = landing_point['x']
#         dy = landing_point['y']
#         dz = landing_point['z']
#
#         # 1) 현재 NED 위치 조회
#         pos = self._client.get_local_position()  # {'x', 'y', 'z'}
#         curr_x, curr_y, curr_z = pos['x'], pos['y'], pos['z']
#
#         # 2) 목표 절대 위치 계산
#         target_x = curr_x + dx
#         target_y = curr_y + dy
#         # 지면(z=0) 기준이라면 dz 그대로 사용, 필요시 고도 유지(예: dz+1.0)
#         target_z = dz
#
#         self._logger.info(
#             "Precision landing → approach to (%.2f, %.2f) at alt %.2f",
#             target_x, target_y, curr_z
#         )
#
#         # ---------------------- Approach (수평 이동) ---------------------- #
#         # setpoint 스트림이 유지되는 상태에서 반복 전송
#         while True:
#             self._client.send_setpoint(target_x, target_y, curr_z)
#             p = self._client.get_local_position()
#             if (abs(p['x'] - target_x) < self.XY_TOL and
#                 abs(p['y'] - target_y) < self.XY_TOL):
#                 break
#             time.sleep(0.1)
#         self._logger.info("Approach complete → horizontal tolerance reached")
#
#         # ---------------------- Descent (단계별 하강) ---------------------- #
#         current_alt = curr_z
#         while current_alt > target_z:
#             next_alt = max(current_alt - self.DESCENT_STEP, target_z)
#             self._client.send_setpoint(target_x, target_y, next_alt)
#             time.sleep(self.STEP_DELAY)
#             current_alt = next_alt
#         self._logger.info(
#             "Descent complete → final altitude %.2f reached", target_z
#         )
#
#         # ---------------------- Final LAND 명령 ---------------------- #
#         self._logger.info("Sending LAND command to autopilot")
#         self._client.master.mav.command_long_send(
#             self._client.target_system,
#             self._client.target_component,
#             mavutil.mavlink.MAV_CMD_NAV_LAND,
#             0,
#             0, 0, 0, 0,
#             target_x, target_y, target_z
#         )
#         self._logger.info("Precision landing sequence initiated")
#
# class DetectManager(BaseManager,Singleton):
#     CONF_THRESH = 0.6
#     FPS_LIMIT = 15.0
#
#     def __init__(self):
#         super(DetectManager, self).__init__()
#
#         #---------------------- 외부 인스턴스 초기화----------------------#
#         ## _client, _config -> MAVLink 클라이언트 인스턴스 및 설정
#         ## _logger -> 로거 초기화
#         ## _detector -> 카메라 및 모델 초기화
#         ## ed.subscribe -> "hold_ready" 이벤트 수신 시 _on_hold_ready 호출
#         #----------------------                ----------------------#
#         self._client = MavLinkClient.get_instance()
#         self._config = self._client.config
#         self._logger = logging.getLogger(self.__class__.__name__)
#         self._detector = Detector()
#         self.ed.subscribe("hold_ready", self._on_hold_ready)
#
#         #----------------------내부 인스턴스 초기화----------------------#
#         self._thread = None
#         self._stop_evt = threading.Event()
#
#     def _on_hold_ready(self, _=None):
#         if self._thread and self._thread.is_alive():
#             return
#         self._stop_evt.clear()
#         self._thread = threading.Thread(target=self._detect_loop,
#                                         name="DetectLoop", daemon=True)
#         self._thread.start()
#         #TODO: 카메라와 모델의 초기작업은 프로그램 실행시 되었다는 가정
#         #TODO: 이미 카메라와 모델은 연결되어 있다는 가정
#         #TODO: 그냥 객체 인식 시작하는 프로세스 추가
#         #TODO: 해당 클래스에서는 객체 인식 결과 값을 받아 신뢰도와 클래스별 분류 하는 과정
#         #TODO: 그리고 거리 계산 함수를 사용해 착륙 매니저에게 착륙 위치와 함꼐 publish
#     def _detect_loop(self):
#         while not self._stop_evt.is_set():
#             result = self._detector.infer()
#             if result is None:
#                 time.sleep(1.0 / self.FPS_LIMIT)
#                 continue
#             # "조난자" 라벨 및 신뢰도 검사
#             if result.label == "조난자" and result.confidence >= self.CONF_THRESH:
#                 # TODO: px→NED 거리 계산 (pixel_to_ned 등 사용)
#                 # dx, dy = pixel_to_ned(...)
#                 # landing_point 구성 예시
#                 # landing_point = {"x": dx, "y": dy, "z": 0.0}
#                 landing_point = {"x": 0, "y": 0, "z": 0.0}
#                 # self._logger.info(
#                 #     "Target found: dx=%.2f dy=%.2f conf=%.2f",
#                 #     dx, dy, result.confidence
#                 # )
#                 # 착륙 매니저로 이벤트 발행
#
#                 self.ed.publish("landing_target", landing_point)
#                 break
#
#             time.sleep(1.0 / self.FPS_LIMIT)
#
#     def stop_detection(self):
#         self._stop_evt.set()
#         if self._thread:
#             self._thread.join(timeout=1.0)