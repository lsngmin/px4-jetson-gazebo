from enum import Enum, auto

class MissionState(Enum):
    WAIT = auto()               # 출발 대기(시작 준비)
    ENROUTE_WP1 = auto()        # 경유점1 이동 중
    ARRIVED_WP1 = auto()        # 경유점1 도착
    ENROUTE_WP2 = auto()        # 경유점2 이동 중
    ARRIVED_WP2 = auto()        # 경유점2 도착
    ENROUTE_TARGET = auto()     # 조난자 위치 이동 중
    ARRIVED_TARGET = auto()     # 조난자 위치 도착
    SEARCH_RESCUE = auto()      # 구조/탐색 임무 수행
    RETURN_HOME = auto()        # 귀환(혹은 미션 종료)
    END = auto()                # 종료/후처리
