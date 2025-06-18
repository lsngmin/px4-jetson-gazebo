from abc import ABC, abstractmethod
import logging

from config import Config
from mavlink.mavlinkClient import PymavlinkClient


class MonitorInterface(ABC):
    _mav_client = None
    _config = None

    @classmethod
    def set_mav_client(cls, mav_client: 'PymavlinkClient'):
        cls._mav_client = mav_client

    @classmethod
    def set_config(cls, config: 'Config'):
        cls._config = config

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        if self.__class__._mav_client is None:
            raise ValueError(
                "MAVLink 클라이언트가 설정되어 있지 않습니다. 시스템 초기화 시 MonitorInterface.set_mav_client()를 반드시 먼저 호출해 주세요.")
        if self.__class__._config is None:
            raise ValueError("설정(config)이 주입되지 않았습니다. 시스템 구동 전에 MonitorInterface.set_config()를 반드시 선행해야 합니다.")

        self._mav_client = self.__class__._mav_client
        self._config = self.__class__._config

    def start(self):
        msg_type, log_msg = self._get_monitor_config()
        self._mav_client.subscribe(msg_type, self._handle_message)
        self._logger.info(log_msg)

    @abstractmethod
    def _get_monitor_config(self):
        """
        return (
            'msg_type',
            'log_msg'
        )
        """
        pass

    @abstractmethod
    def _handle_message(self, msg):
        pass

    @abstractmethod
    def set_trigger_callback(self, callback):
        """
        조건 충족(또는 미충족) 시 호출될 콜백을 등록하는 함수.
        """
        pass