from ultralytics import YOLO

CLASS_NAMES = ['tray', 'landing marker', 'V marker', 'ArUco Marker']

class YoloPredictor:
    def __init__(self, model_path='best.torchscript', imgsz=832, conf=0.75, iou=0.45, show=False):
        self.model = YOLO(model_path)
        self.imgsz = imgsz
        self.conf = conf
        self.iou = iou
        self.show = show

    def infer(self, source=0):
        results = self.model(
            source=source,
            conf=self.conf,
            iou=self.iou,
            imgsz=self.imgsz,
            show=self.show,
            stream=True
        )

        detections = []

        for r in results:
            for box in r.boxes:
                xyxy = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                cls_id = int(box.cls[0].item())
                label = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else str(cls_id)

                detection = {
                    'label': label,
                    'conf': conf,
                    'bbox': xyxy
                }
                print(f"[Detected] class: {label}, conf: {conf:.2f}, bbox: {xyxy}")
                detections.append(detection)

        return detections

if __name__ == '__main__':
    predictor = YoloPredictor()
    predictor.infer(source=0)

