import time

from ultralytics import YOLO            # pip install ultralytics
import cv2

from common.geometry import xywh_to_uv

#모델 불러오기
#경로는 config에 넣어서 가져와
model = YOLO("yolov8n.pt")

#카메라 프레임 읽기
#카메라 연결 로직을 만들고 cap에 담는 구조로 가면 되겠네
cap = cv2.VideoCapture(0)
while True:
    ok, frame = cap.read()
    if not ok:
        break
        #카메라가 연결되지 않았을 때 break
    #아래는 리스트를 리턴해준다, [0]은 그 중 첫 프레임의 result 객체를 하나 꺼내는 것이고
    #result.boxes 에 좌표가 들어있을듯
    #model에 넣어지는 frame은 영상 속의 한 장의 프레임(사진) frame이 많으면 많을 수록 여러개의 result 값을 반환한다.
    #result는 한장의 사진 속에 모델이 검출한 객체의 정보가 담겨져 있다
    #검출한 객체가 여러개이면 여러개가 있다
    result = model(frame)[0]

    #아래도 config로 지정해서 받아오면 될듯
    target_name = "rescue" # 모델할 때 라벨링한 이름이다
    target_cls_id = model.names.index(target_name) # 라벨링한 이름이 몇번째 인덱스로 등록되어 있는지 확인

    #객체가 검출한 수가 여러개일 수 있으니 하나씩 까보자
    for box in result.boxes:
        cls_id = int(box.cls[0]) #박스가 탐지한 클래스 아이디 타겟이랑 비교해야지
        conf = float(box.conf[0]) #모델이 찾은 박스의 신뢰도 일듯
        if cls_id == target_cls_id and conf >= 0.3:
            x, y, w, h = box.xywh[0]
            u, v = xywh_to_uv(x, y, w, h)
            print(x, y, w, h)

            cv2.rectangle(frame, (int(x - w/2), int(y - h/2)),
                      (int(x + w/2), int(y + h/2)),
                      (0, 255, 0), 2)
            cv2.circle(frame, (int(u), int(v)), 3, (0, 0, 255), -1)
            print(f"찾은 물체 중심 픽셀   u={u:.1f}, v={v:.1f}")
    cv2.imshow("vision", frame)
    #객체 인식이 안되면 아래 sleep 조정해서 ㄱㄱ
    time.sleep(3)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC 누르면 종료
        break

cap.release()
cv2.destroyAllWindows()
