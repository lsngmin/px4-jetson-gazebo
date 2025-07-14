import time, logging

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field

from common.core import MavLinkClient
from YoloPredictor import YOLOPredictor
import cv2

class DetectionResult(BaseModel):
    x: int = Field(..., description="이미지 상의 x 좌표")
    y: int = Field(..., description="이미지 상의 y 좌표")
    confidence: float = Field(..., ge=0.0, le=1.0, description="탐지 신뢰도 (0~1 사이)")
    label: str = Field(..., description="객체 클래스 이름")

    width: Optional[int] = Field(None, description="바운딩 박스 너비")
    height: Optional[int] = Field(None, description="바운딩 박스 높이")
    world_x: Optional[float] = Field(None, description="실세계 x 좌표 (예: GPS 또는 meter)")
    world_y: Optional[float] = Field(None, description="실세계 y 좌표")


class DetectorInterface(ABC):
    """
    객체 인식은 총 3가지로 알고 있습니다.
    하기 버티포트, 조난자 하기 버티포트, 조난자 3가지를 인식하는
    하나의 모델을 사용합니다.

    객체 인식 클래스 구현하실 때 상속하셔서 구현하시면 됩니다.
    """

    @abstractmethod
    def detect(self, frame) -> List[DetectionResult]:
        """
        하나의 프레임에서 각각의 객체를 인식합니다.
        매개변수 frame 은 영상 프레임을 제공받습니다.

        카메라 연결 로직 구현 후 while문에 detect에 프레임을 담아서 호출 하면됩니다.
        반환값은 List[DetectionResult] 이 형태입니다.
        DetectionResult는 데이터 클래스이고
        해당 클래스 안에는 x,y, confidence, label 필드가 있습니다.
        x, y -> 객체가 이미지에 발견된 위치입니다.(픽셀 좌표 기준으로 반환하시면 됩니다.)
        confidence -> 객체를 탐지한 신뢰도 입니다.
        label -> 어떤 객체 인지 네이밍 해주시면 됩니다. enum으로 정의하셔 반환하셔도 됩니다.
        """

        pass


class Detector:
    def __init__(self):
        self._client = MavLinkClient.get_instance()
        self._config = self._client.config
        self._logger = logging.getLogger(self.__class__.__name__)

        # resolveTODO: 카메라 연결 부분 구현
        self._camera_src = self._config.camera_src
        # self.cap = cv2.VideoCapture(self._camera_src, cv2.CAP_ANY)
        # if not self.cap.isOpened():
        #     raise RuntimeError(f"카메라 연결 실패: {self._camera_src!r}")
        self._logger.info("Camera opened: %s", self._camera_src)

        # TODO: 모델 로드 구현 (o)

        self.model = YoloPredictor(model_path="best.torchscript", imgsz=832, conf=0.5, show=False)


    def detect(self, frame) -> List[DetectionResult]:
        # TODO: 실제 모델을 프레임 속에 올려 객체 인식하는 핵심 부분입니다. (O)

        results = self.model.infer(source=frame)
        detections = []

        for det in results:
            x1, y1, x2, y2 = det["bbox"]
            x_center = int((x1 + x2) / 2)
            y_center = int((y1 + y2) / 2)
            width = int(x2 - x1)
            height = int(y2 - y1)
                
            detections.append(
                DetectionResult(
                    x=x_center,
                    y=y_center,
                    confidence=det["conf"],
                    label=det["label"]
                )
            )

        # TODO: 각 리스트 요소에 인식할 객체의 파라미터를 결정해 넣어주시면 됩니다. (O)
        return detections


    def infer(self) -> DetectionResult:
        ret, frame = self.cap.read()
        if not ret:
            self._logger.warning("Frame read failed")
            return None
        return self.detect(frame)


class Model:
    def __init__(self, model_path: str = "/home/azure/oje36/best.trt"):
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
