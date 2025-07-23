import time

from typing import Optional

import cv2
from pydantic import BaseModel, Field
from typing_extensions import override
from ultralytics import YOLO

from common.YoloPredictor import YoloPredictor
from common.pattern import Singleton
from default import VISION_UV
from common.geometry import xywh_to_uv
from common.messages import UV
from layer.monitor.base import Monitor

class DetectionResult(BaseModel):
    u: int = Field(..., description="이미지 상의 x 좌표")
    v: int = Field(..., description="이미지 상의 y 좌표")
    confidence: float = Field(..., ge=0.0, le=1.0, description="탐지 신뢰도 (0~1 사이)")
    label: str = Field(..., description="객체 클래스 이름")

    width: Optional[int] = Field(None, description="바운딩 박스 너비")
    height: Optional[int] = Field(None, description="바운딩 박스 높이")
    world_x: Optional[float] = Field(None, description="실세계 x 좌표 (예: GPS 또는 meter)")
    world_y: Optional[float] = Field(None, description="실세계 y 좌표")


class Detector(Singleton, Monitor):
    def __init__(self):
        super().__init__('HEARTBEAT')

        # resolveTODO: 카메라 연결 부분 구현
        self._camera_src = self._config.camera_src
        self._yopd = YoloPredictor()
        self._model = self._yopd.model
        self.cap = cv2.VideoCapture(0, cv2.CAP_ANY)
        if not self.cap.isOpened():
            raise RuntimeError(f"카메라 연결 실패: {self._camera_src!r}")
        self._logger.info("Camera opened: %s", self._camera_src)
        self._target_name = self._config.rescue_target_name  # 모델할 때 라벨링한 이름이다
        # self._target_cls_id = self._model.names.index(self._target_name)

        names_dict = self._model.names
        # label → id 매핑 생성
        name2id = {v: k for k, v in names_dict.items()}
        self._target_cls_id = name2id[self._target_name]

        self._logger.info("디텍더 초기화 완료")

    def infer(self) -> None:
        while True:
            ok, frame = self.cap.read()
            if not ok:
                self._logger.warning("카메라 연결 설정 불량.")
                break
                # 카메라가 연결되지 않았을 때 break
            # 아래는 리스트를 리턴해준다, [0]은 그 중 첫 프레임의 result 객체를 하나 꺼내는 것이고
            # result.boxes 에 좌표가 들어있을듯
            # model에 넣어지는 frame은 영상 속의 한 장의 프레임(사진) frame이 많으면 많을 수록 여러개의 result 값을 반환한다.
            # result는 한장의 사진 속에 모델이 검출한 객체의 정보가 담겨져 있다
            # 검출한 객체가 여러개이면 여러개가 있다
            # 객체가 검출한 수가 여러개일 수 있으니 하나씩 까보자
            result = self._model(frame)[0]
            if not result:
                self._logger.warning("객체가 검출되지 않았습니다.")
            for box in result.boxes:
                cls_id = int(box.cls[0])  # 박스가 탐지한 클래스 아이디 타겟이랑 비교해야지
                conf = float(box.conf[0])  # 모델이 찾은 박스의 신뢰도 일듯
                self._logger.debug(f"cls_id: {cls_id}, conf: {conf}")
                if cls_id == self._target_cls_id and conf >= self._config.meet_confidence:
                    x, y, w, h = box.xywh[0]
                    u, v = xywh_to_uv(x, y, w, h)
                    self._logger.debug(x, y, w, h)
                    self._logger.debug(u, v)
                    self._ed.publish(VISION_UV, UV(u, v))
                    self._logger.info(f"객체 검출 성공: u -> {u}, v -> {v}, conf -> {conf}, label -> {self._target_name}")
            self._logger.warning("객체가 검출되었으나 해당하는 객체가 아닙니다.")

    @override
    def _handle_message(self, msg):
        pass

class Model:
    def __init__(self, model_path: str = None):
        # self.model = yolov8.load(model_path)
        self.model = None
        time.sleep(0.1)

    def infer(self, frame) -> DetectionResult:
        h, w = frame.shape[:2]
        # 스텁: 프레임 중앙에 "조난자" 발생
        return DetectionResult(
            label="조난자",
            cx=w / 2,
            cy=h / 2,
            confidence=1.0,
            width=w,
            height=h
        )