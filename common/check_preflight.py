import logging, time

from pymavlink import mavutil

from common import Singleton
from common.core import MavLinkClient

class CheckPreflight(Singleton):
    def __init__(self):
        self._client = MavLinkClient.get_instance()
        self._config = self._client.config
        self._logger = logging.getLogger(self.__class__.__name__)

    def wait_for_px4_standby(self):
        self._logger.info("PX4가 STANDBY(대기) 상태가 될 때까지 기다립니다.")
        timeout = 60
        t0 = time.time()
        while time.time() - t0 < timeout:
            hb = self._client.master.recv_match(type='HEARTBEAT', blocking=True, timeout=1)
            if hb:
                state = hb.system_status
                self._logger.info(f" - 현재 HEARTBEAT system_status={state}")
                if state == mavutil.mavlink.MAV_STATE_STANDBY:
                    self._logger.info("PX4가 STANDBY 상태입니다. (비행 준비 완료)")
                    return True
            else:
                self._logger.warning(f" - 하트비트 신호 없음 (기체 연결 대기 중)")
        self._logger.error("PX4가 STANDBY 상태로 전환되지 않았습니다. (타임아웃)")
        return False

    def sensor_bits_to_names(self, bits):
        SENSOR_FLAGS = [
            (0, 'GYRO'), (1, 'ACCEL'), (2, 'MAG'), (3, 'ABS_PRESSURE'), (4, 'DIFF_PRESSURE'),
            (5, 'GPS'), (6, 'OPTICAL_FLOW'), (7, 'VISION_POSITION'), (8, 'LASER_POSITION'),
            (9, 'EXTERNAL_GROUND_TRUTH'), (10, 'ANGULAR_RATE_CONTROL'), (11, 'ATTITUDE_STABILIZATION'),
            (12, 'YAW_POSITION'), (13, 'Z_ALTITUDE_CONTROL'), (14, 'XY_POSITION_CONTROL'),
            (15, 'MOTOR_OUTPUTS'), (16, 'RC_RECEIVER'), (17, '3D_GYRO2'), (18, '3D_ACCEL2'),
            (19, '3D_MAG2'), (20, 'GEOFENCE'), (21, 'AHRS'), (22, 'TERRAIN'), (23, 'REVERSE_MOTOR'),
            (24, 'LOGGING'), (25, 'BATTERY'), (26, 'PROXIMITY'), (27, 'SATCOM'), (28, 'PRECLAND'),
            (29, 'OBSTACLE_AVOIDANCE'), (30, 'PROP_ENC'), (31, 'UNKNOWN31')
        ]
        return [name for i, name in SENSOR_FLAGS if bits & (1 << i)]

    def sys_status_check(self):
        self._logger.info("센서 상태(SYS_STATUS) 점검을 시작합니다.")
        msg = self._client.master.recv_match(type='SYS_STATUS', blocking=True, timeout=5)
        if not msg:
            self._logger.error("SYS_STATUS 메시지를 받지 못했습니다! (기체 연결 또는 통신 상태를 확인하세요)")
            return False
        healthy = msg.onboard_control_sensors_health
        enabled = msg.onboard_control_sensors_enabled
        enabled_names = self.sensor_bits_to_names(enabled)
        healthy_names = self.sensor_bits_to_names(healthy)
        unhealthy = set(enabled_names) - set(healthy_names)
        self._logger.info(f" - 활성(ENABLED) 센서: {enabled_names}")
        self._logger.info(f" - 정상(HEALTHY) 센서: {healthy_names}")
        if not unhealthy:
            self._logger.info("모든 활성 센서가 정상입니다. (비행 가능)")
            return True
        if unhealthy == {"RC_RECEIVER"}:
            self._logger.warning("RC_RECEIVER(송신기) 비정상 → RC 미사용 환경이므로 무시하고 계속 진행합니다.")
            return True
        self._logger.error(f"다음 센서가 활성화돼 있으나 비정상 상태입니다: {list(unhealthy)}")
        return False

    def wait_for_gps_fix(self):
        self._logger.info("GPS 신호 수신(GPS fix) 대기 중.")
        timeout = 60
        t0 = time.time()
        while time.time() - t0 < timeout:
            msg = self._client.master.recv_match(type='GPS_RAW_INT', blocking=True, timeout=2)
            if msg and msg.fix_type >= 3:
                self._logger.info(f"GPS fix 확보. (fix_type={msg.fix_type}, 위성 수={msg.satellites_visible})")
                return True
            else:
                self._logger.info(f" - GPS 고정 대기 중. (아직 정확한 위치 확보 전)")
        self._logger.error("제한 시간 내 GPS fix 확보에 실패했습니다.")
        return False

    def start(self):
        self._client.master.wait_heartbeat(timeout=10)

        if not self.wait_for_px4_standby():
            self._logger.error("PX4가 정상 대기(STANDBY) 상태가 아닙니다. (기체 상태를 확인하세요.)")
            exit(1)

        if not self.sys_status_check():
            self._logger.error("센서 이상 (비정상 센서가 존재합니다.)")
            exit(1)

        if not self.wait_for_gps_fix():
            self._logger.error("GPS 신호를 확보하지 못했습니다. (실외, 시뮬 환경 등 GPS 확인 필요)")
            exit(1)
