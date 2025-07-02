from enum import Enum

class EdgeType(Enum):
    RISING_EDGE = 0 
    FALLING_EDGE = 1

class TriggerType(Enum):
    NONE = 0
    AUTO = 1
    NORMAL = 2
    SINGLE = 3

class Trigger:
    def __init__(self) -> None:
        self._edge_type: EdgeType = EdgeType.RISING_EDGE
        self._trigger_type: TriggerType = TriggerType.NONE
        self._trigger_height: int = 0

    @property
    def trigger_height(self) -> int: return self._trigger_height

    @property
    def edge_type(self) -> EdgeType: return self._edge_type

    @property
    def trigger_type(self) -> TriggerType: return self._trigger_type

    @edge_type.setter
    def edge_type(self, edge_type: EdgeType): self._edge_type = edge_type

    @trigger_type.setter
    def trigger_type(self, trigger_type: TriggerType): self._trigger_type = trigger_type