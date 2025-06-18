from abc import ABC, abstractmethod
import logging

from core import MavLinkClient

class MonitorInterface(ABC):
    def __init__(self):
        self._client = MavLinkClient.get_instance()
        self._config = self._client.config
        self._logger = logging.getLogger(self.__class__.__name__)

    def start(self):
        msg_type, log_msg = self._get_monitor_config()
        self._client.subscribe(msg_type, self._handle_message)
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