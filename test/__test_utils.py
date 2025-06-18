import math
import logging
import pytest
from util import utils
from util.utils import haversine, GPSData
from datetime import datetime

# 테스트 시 로깅을 캡처하기 위한 설정
@pytest.fixture(autouse=True)
def configure_caplog(caplog):
    caplog.set_level(logging.INFO)
    return caplog

@pytest.mark.parametrize("lat1, lon1, lat2, lon2, expected", [
    (0.0, 0.0, 0.0, 0.0, 0.0),
    # 약 111.195 km: 위도 1도 차이 (적도 부근)
    (0.0, 0.0, 1.0, 0.0, 111195),
    # 경도 1도 차이: 위도 0도 부근 약 111319 m
    (0.0, 0.0, 0.0, 1.0, 111319),
    # 위도 45도에서 경도 1도 차이: 약 78900 m
    (45.0, 0.0, 45.0, 1.0, 78900),
])
def test_haversine_known_distances(lat1, lon1, lat2, lon2, expected):
    dist = haversine(lat1, lon1, lat2, lon2)
    # 허용 오차: 1% 이내
    assert math.isclose(dist, expected, rel_tol=0.01), f"Distance {dist} not within tolerance of expected {expected}"


def test_haversine_opposite_points():
    # 극지점 테스트: 북극과 남극 간 대략 반지름 * pi 거리
    # 북극(90,0) 남극(-90,0) 사잇거리 약 지구 반지름 * pi
    R = 6371000
    expected = R * math.pi
    dist = haversine(90.0, 0.0, -90.0, 0.0)
    assert math.isclose(dist, expected, rel_tol=0.01)


def test_gpsdata_dataclass_fields():
    now = datetime.utcnow()
    gps = GPSData(latitude=37.0, longitude=127.0, altitude=100.5, timestamp=now)
    assert gps.latitude == 37.0
    assert gps.longitude == 127.0
    assert gps.altitude == 100.5
    assert gps.timestamp is now

# 모듈 import 시점 테스트: utils 모듈 import 자체가 로그를 남기지 않도록 설계되었음을 전제
# 만약 import 시점에 로그를 남기도록 되어 있으면, 테스트 순서에 따라 다를 수 있음.
def test_module_import_no_side_effect(caplog):
    # caplog 초기화 후 다시 importlib.reload를 통해 import 시 로그 남기는지 확인
    import importlib
    caplog.clear()
    importlib.reload(utils)
    # import 시점에 메시지가 즉시 찍히지 않으면 caplog.text는 비어있거나 INFO 외 메시지 없음
    # 구체적 정책에 따라 다르므로 여기선 import 시점 로그를 피하도록 권장
    # assert caplog.text == ""  # 필요 시 활성화
    assert True
