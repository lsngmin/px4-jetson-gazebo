from abc import ABC, abstractmethod
import logging

from core import MavLinkClient

class ControlInterface(ABC):
    def __init__(self):
        self._client = MavLinkClient.get_instance()
        self._config = self._client.config
        self._logger = logging.getLogger(self.__class__.__name__)

    def start_with_callback(self, callback):
        self._register_callback(callback)
        return self

    @abstractmethod
    def _register_callback(self, callback):
        pass