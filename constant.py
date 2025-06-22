from enum import IntEnum, Enum, auto

class LandedStateEnum(IntEnum):
    UNDEFINED = 0      # 판단 불가
    ON_GROUND = 1      # 지상 고정
    IN_AIR    = 2      # 공중 (순항·호버 포함)
    TAKEOFF   = 3      # 이륙 단계
    LANDING   = 4      # 착륙 단계

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

class MainMode(IntEnum):
    MANUAL      = 1
    ALTCTL      = 2
    POSCTL      = 3
    AUTO        = 4
    ACRO        = 5
    OFFBOARD    = 6
    STABILIZED  = 7
    RATTITUDE   = 8


class AutoSubMode(IntEnum):
    READY         = 1
    TAKEOFF       = 2
    LOITER        = 3   # QGC “Hold”
    MISSION       = 4
    RTL           = 5
    LAND          = 6
    RTGS          = 7

class VtolStateEnum(IntEnum):
    UNDEFINED = 0
    MC = 3
    FW = 4
    TRANSITION_TO_FW = 1
    TRANSITION_TO_MC = 2
    ENUM_END = 5


def decode_px4_mode(raw: int) -> str:
    """Return 'MAIN' 또는 'AUTO:SUB' 문자열."""
    main_val = (raw >> 16) & 0xFF
    sub_val  = (raw >> 24) & 0xFF

    try:
        main = MainMode(main_val).name
    except ValueError:
        return f"UNKNOWN_MAIN({main_val})"

    if main == "AUTO":
        try:
            sub = AutoSubMode(sub_val).name
        except ValueError:
            sub = f"UNK_SUB({sub_val})"
        return f"{main}:{sub}"
    return main