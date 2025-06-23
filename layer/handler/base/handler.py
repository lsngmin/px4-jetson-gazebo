import logging

from common import MEventDispatcher, M2EventDispatcher
from common.core import MavLinkClient

class Handler:
    def __init__(self) -> None:
        self._ed: MEventDispatcher = MEventDispatcher.instance()
        self._toc: M2EventDispatcher = M2EventDispatcher.instance()
        self._client: MavLinkClient = MavLinkClient.get_instance()
        self._config = self._client.config
        self._logger = logging.getLogger(self.__class__.__name__)
