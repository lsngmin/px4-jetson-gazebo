from typing import List

from detect import DetectorInterface, DetectionResult


class Detector(DetectorInterface):
    def __init__(self):
        # TODO: 모델 로드 구현
        # TODO: 카메라 연결 부분 구현
        pass

    def detect(self, frame) -> List[DetectionResult]:
        # TODO: 실제 모델을 프레임 속에 올려 객체 인식하는 핵심 부분입니다.
        return [
            # TODO: 각 리스트 요소에 인식할 객체의 파라미터를 결정해 넣어주시면 됩니다.
            DetectionResult(x=100, y=200, confidence=0.92, label='rescue_target'),
            DetectionResult(x=250, y=300, confidence=0.87, label='vertiport1'),
            DetectionResult(x=250, y=300, confidence=0.87, label='vertiport2')
        ]