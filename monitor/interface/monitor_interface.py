from abc import ABC, abstractmethod
import logging

from core import MavLinkClient

class MonitorInterface(ABC):
    def __init__(self):
        self._client = MavLinkClient.get_instance()
        self._config = self._client.config
        self._logger = logging.getLogger(self.__class__.__name__)

    def start_with_callback(self, callback):
        msg_type, log_msg = self._get_monitor_config()
        self._client.subscribe(msg_type, self._handle_message)
        self._logger.info(log_msg)
        self._register_callback(callback)
        return self

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
    def _register_callback(self, callback):
        pass