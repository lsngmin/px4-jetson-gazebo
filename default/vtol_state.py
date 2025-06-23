from enum import IntEnum

class VtolStateEnum(IntEnum):
    UNDEFINED = 0
    MC = 3
    FW = 4
    TRANSITION_TO_FW = 1
    TRANSITION_TO_MC = 2
    ENUM_END = 5