from default import MainMode
from common.pattern import Singleton
from vision.detect import Detector
from common.geometry import uv_depth_to_cam
from layer.handler.base import Handler

class DetectStartHandler(Handler, Singleton):
    def __init__(self):
        super().__init__()

    def _on_authority_activated(self):
        checked = self._is_vtol_mc and self._current_mode is MainMode.OFFBOARD and self._is_rescue_reached
        if checked and not self._is_authority_active:
            if self._uv is not None:
                pt_cam = uv_depth_to_cam(self._uv, self.current['z'])
                print("카메라 좌표 (Xc, Yc, Zc) =", pt_cam)

            best_confidence = self._config.meet_confidence
            while True:
                dectectionresult = self._detector.infer()

                #낮다면 다시 한번 루프를 돌려야함

            #TODO 조난자 위치에 있으며 Offboard인 상황
            # 이제 객체 인식을 시작해야함
            self._is_authority_active = checked