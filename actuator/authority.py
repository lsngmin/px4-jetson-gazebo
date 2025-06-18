# from common.singleton_mixin import SingletonMixin
#
#
# class AuthorityActuator(SingletonMixin):
#     def __init__(self, mav_client):
#         SingletonMixin.__init__(self)
#         self._mav_client = mav_client
#
#     def set_offboard_mode(self):
#         # PX4의 base_mode / custom_mode 정의 참고
#         PX4_CUSTOM_MODE_OFFBOARD = 6
#         self._mav_client.master.set_mode_apm(PX4_CUSTOM_MODE_OFFBOARD)
#         # 또는 직접 MAVLink SET_MODE 명령 전송도 가능:
#         # self._mav_client.master.mav.set_mode_send(
#         #     self._mav_client.master.target_system,
#         #     mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
#         #     PX4_CUSTOM_MODE_OFFBOARD
#         # )
