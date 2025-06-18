from enum import IntEnum


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