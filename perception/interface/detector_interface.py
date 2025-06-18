from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field

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



