import logging
from abc import ABC, abstractmethod

from common.core import MavLinkClient
from common.pattern import MEventDispatcher

class Monitor(ABC):
    def __init__(self, msg_type):
        self._client = MavLinkClient.get_instance()
        self._config = self._client.config
        self._ed: MEventDispatcher = MEventDispatcher.instance()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._client.subscribe(msg_type, self._handle_message)

    @abstractmethod
    def _handle_message(self, msg):
        pass

