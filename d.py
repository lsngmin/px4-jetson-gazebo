from pymavlink import mavutil
import time
import threading

def monitor_statustext(master, duration=10):
    t0 = time.time()
    while time.time() - t0 < duration:
        msg = master.recv_match(type='STATUSTEXT', blocking=True, timeout=2)
        if msg:
            print(f"[STATUSTEXT][{msg.severity}] {msg.text.strip()}")

def sensor_bits_to_names(bits):
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

def sys_status_check(master):
    print("[INFO] Checking SYS_STATUS...")
    msg = master.recv_match(type='SYS_STATUS', blocking=True, timeout=5)
    if not msg:
        print("[ERROR] No SYS_STATUS received!")
        return False
    healthy = msg.onboard_control_sensors_health
    enabled = msg.onboard_control_sensors_enabled
    enabled_names = sensor_bits_to_names(enabled)
    healthy_names = sensor_bits_to_names(healthy)
    unhealthy = set(enabled_names) - set(healthy_names)
    print(f"[INFO] 센서 ENABLED  : {enabled_names}")
    print(f"[INFO] 센서 HEALTHY : {healthy_names}")
    if not unhealthy:
        print("[OK] 모든 ENABLED 센서 정상!")
        return True
    if unhealthy == {"RC_RECEIVER"}:
        print("[WARN] RC_RECEIVER만 unhealthy → 무시하고 진행")
        return True
    print(f"[FAIL] 이하 센서 ENABLED인데 HEALTHY 아님: {list(unhealthy)}")
    return False

def wait_for_px4_standby(master, timeout=60):
    print("[INFO] Waiting for PX4 to reach STANDBY...")
    t0 = time.time()
    while time.time() - t0 < timeout:
        hb = master.recv_match(type='HEARTBEAT', blocking=True, timeout=1)
        if hb:
            state = hb.system_status
            print(f"  HEARTBEAT system_status={state}")
            if state == mavutil.mavlink.MAV_STATE_STANDBY:
                print("→ PX4 is now STANDBY!")
                return True
            monitor_statustext(master, duration=3)
        else:
            print("  No heartbeat")
    print("✗ Timeout waiting for STANDBY")
    return False

def wait_for_gps_fix(master, timeout=60):
    print("[INFO] Waiting for GPS fix...")
    t0 = time.time()
    while time.time() - t0 < timeout:
        msg = master.recv_match(type='GPS_RAW_INT', blocking=True, timeout=2)
        if msg and msg.fix_type >= 3:
            print(f"[OK] GPS fix_type={msg.fix_type}, satellites={msg.satellites_visible}")
            return True
        else:
            print("  Waiting for GPS fix...")
    print("✗ Timeout waiting for GPS fix")
    return False

def send_setpoint(master, alt, repeat=50, sleep=0.02):
    for _ in range(repeat):
        now_ms = int(time.time() * 1000) % 0xFFFFFFFF
        master.mav.set_position_target_local_ned_send(
            now_ms,  # 밀리초 단위로 변환!
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b0000111111111000,
            0, 0, -alt,  # x, y, z
            0, 0, 0,     # vx, vy, vz
            0, 0, 0,     # ax, ay, az
            0, 0         # yaw, yaw_rate
        )
        time.sleep(sleep)

def set_offboard_mode(master):
    print("[INFO] Switching to OFFBOARD mode...")
    base_mode = mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED
    main_mode = 6  # PX4_CUSTOM_MAIN_MODE_OFFBOARD
    sub_mode = 0
    master.set_mode_px4(base_mode, main_mode, sub_mode)
    print("→ Mode set to OFFBOARD")

def arm_drone(master, timeout=10):
    print("[INFO] Sending arm command...")
    master.arducopter_arm()
    t0 = time.time()
    while time.time() - t0 < timeout:
        hb = master.recv_match(type='HEARTBEAT', blocking=True, timeout=1)
        if hb and (hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED):
            print("→ Drone is now ARMED")
            return True
        print("...waiting for ARM")
    print("✗ Arm failed (timeout)")
    return False

def send_takeoff(master, alt=3.0):
    print(f"[INFO] Sending takeoff command (alt={alt}m)...")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, 0, alt
    )
    print("→ Takeoff command sent!")
def gradual_takeoff(master, start_z=0.0, target_z=-3.0, steps=100, dt=0.05):
    """현재 위치에서 z=target_z까지 점진적으로 이동(setpoint)"""
    for i in range(steps):
        z = start_z + (target_z - start_z) * (i + 1) / steps
        now_ms = int(time.time() * 1000) % 0xFFFFFFFF
        master.mav.set_position_target_local_ned_send(
            now_ms,
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b0000111111111000,
            0, 0, z,     # x, y, z (z는 점진적으로 감소)
            0, 0, 0,     # vx, vy, vz
            0, 0, 0,     # ax, ay, az
            0, 0         # yaw, yaw_rate
        )
        time.sleep(dt)

def offboard_watchdog(master, target_z_func, sleep=0.05):
    """
    target_z_func: 호출 시점에 목표 z값을 반환하는 함수
    """
    while True:
        now_ms = int(time.time() * 1000) % 0xFFFFFFFF
        z = target_z_func()
        master.mav.set_position_target_local_ned_send(
            now_ms,
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b0000111111111000,
            0, 0, z,
            0, 0, 0,
            0, 0, 0,
            0, 0
        )
        time.sleep(sleep)
current_z = 0.0

def target_z_func():
    return current_z

# =================
# 메인 플로우
# =================
if __name__ == "__main__":
    master = mavutil.mavlink_connection('udp:0.0.0.0:14551')
    master.wait_heartbeat(timeout=10)

    if not wait_for_px4_standby(master, timeout=60):
        print("[ABORT] PX4 not ready. See STATUSTEXT above.")
        exit(1)

    if not sys_status_check(master):
        monitor_statustext(master, duration=10)
        print("[ABORT] Sensor health problem.")
        exit(1)

    if not wait_for_gps_fix(master, timeout=60):
        monitor_statustext(master, duration=10)
        print("[ABORT] GPS fix not acquired.")
        exit(1)

    # 4. OFFBOARD 전 setpoint 워밍업(1초)
    send_setpoint(master, alt=30.0, repeat=50, sleep=0.02)

    # 5. OFFBOARD 모드 진입
    set_offboard_mode(master)

    # 6. Arm 시도
    if not arm_drone(master, timeout=10):
        monitor_statustext(master, duration=10)
        print("[ABORT] Arm failed.")
        exit(1)

    # 7. (중요!) 오프보드 워치독 스레드로 setpoint 반복 송신
    offboard_thread = threading.Thread(target=offboard_watchdog, args=(master, target_z_func, 0.05), daemon=True)
    offboard_thread.start()

    # 8. 점진적 이륙: current_z를 0에서 -3.0으로 천천히 내려준다!
    for i in range(100):
        current_z = 0.0 + (-30.0 - 0.0) * (i + 1) / 100
        time.sleep(0.05)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("프로그램 수동 종료!")

