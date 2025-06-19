from pymavlink import mavutil
import time
import threading

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

