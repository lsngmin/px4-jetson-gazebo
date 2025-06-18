from enum import IntEnum

class LandedStateEnum(IntEnum):
    UNDEFINED = 0      # 판단 불가
    ON_GROUND = 1      # 지상 고정
    IN_AIR    = 2      # 공중 (순항·호버 포함)
    TAKEOFF   = 3      # 이륙 단계
    LANDING   = 4      # 착륙 단계
