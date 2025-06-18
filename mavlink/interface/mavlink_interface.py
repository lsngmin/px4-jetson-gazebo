from abc import ABC, abstractmethod
from typing import Callable, Any

class MavlinkClientInterface(ABC):
    @abstractmethod
    def subscribe(self, msg_type: str, callback: Callable[[Any], None]) -> None:
        """
        Register a callback for a MAVLink message type.
        :param msg_type: MAVLink message type name (e.g. 'EXTENDED_SYS_STATE')
        :param callback: Function accepting one argument (the MAVLink message object)
        """
        ...
