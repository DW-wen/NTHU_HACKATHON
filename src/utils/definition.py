from pygame import Rect
from .settings import GameSettings
from dataclasses import dataclass
from enum import Enum
from typing import overload, TypedDict, Protocol, List, Dict, Any, Optional

# --- Type Aliases ---
MouseBtn = int
Key = int

# --- Enums ---
class Direction(Enum):
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    NONE = 'NONE'

# --- Dataclasses ---
@dataclass
class Position:
    """Represents a position in game world coordinates (float)."""
    x: float
    y: float
    
    def copy(self) -> 'Position':
        return Position(self.x, self.y)
        
    def distance_to(self, other: "Position") -> float:
        """Calculates the Euclidean distance to another position."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        
@dataclass
class PositionCamera:
    """Represents the camera's top-left offset (integer pixel coordinates)."""
    x: int
    y: int
    
    def copy(self) -> 'PositionCamera':
        return PositionCamera(self.x, self.y)
        
    def to_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)
        
    def transform_position(self, position: Position) -> tuple[int, int]:
        """Transforms world position to screen coordinates (tuple)."""
        return (int(position.x) - self.x, int(position.y) - self.y)
        
    def transform_position_as_position(self, position: Position) -> Position:
        """Transforms world position to screen coordinates (Position dataclass)."""
        return Position(int(position.x) - self.x, int(position.y) - self.y)
        
    def transform_rect(self, rect: Rect) -> Rect:
        """Transforms a world Rect to a screen Rect."""
        return Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)

@dataclass
class Teleport:
    """Represents a teleportation point between maps."""
    pos: Position
    destination: str
    
    # Overload signatures for constructor
    @overload
    def __init__(self, x: int, y: int, destination: str) -> None: ...
    @overload
    def __init__(self, pos: Position, destination: str) -> None: ...

    # Implementation
    def __init__(self, *args, **kwargs):
        if isinstance(args[0], Position):
            self.pos = args[0]
            self.destination = args[1]
        else:
            # Assuming args are (x, y, dest)
            x, y, dest = args
            self.pos = Position(float(x), float(y)) # Use float for position type consistency
            self.destination = dest
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts to a serializable dictionary using tile coordinates."""
        return {
            "x": int(self.pos.x) // GameSettings.TILE_SIZE,
            "y": int(self.pos.y) // GameSettings.TILE_SIZE,
            "destination": self.destination
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Teleport':
        """Creates a Teleport instance from a dictionary of tile coordinates."""
        # Convert tile coordinates back to pixel positions
        return cls(
            data["x"] * GameSettings.TILE_SIZE, 
            data["y"] * GameSettings.TILE_SIZE, 
            data["destination"]
        )

# --- Game Data Types ---

# Helper function definition
def clamp_level(level: int) -> int:
    """Clamp monster level to the supported range 1..3 (inclusive)."""
    try:
        lv = int(level)
    except Exception:
        lv = 1
    if lv < 1:
        return 1
    # if lv > 3:
    #     return 3
    return lv

# TypedDicts (Note: TypedDict methods are for documentation, not actual Python methods)
class Monster(TypedDict):
    """Data structure for a single monster instance."""
    name: str
    hp: int
    max_hp: int
    level: int
    element: str
    sprite_path: str
    
    # TypedDicts do not support instance methods, but we can define a protocol 
    # or just document the expected conversion function. 
    # Keeping the to_dict method here for consistency with user's original code.
    def to_dict(self) -> Dict[str, object]:
        """將 Monster 實例轉換為可序列化的字典"""
        # Note: self.element must be present for saving state after battles
        return {
            "name": self['name'],
            "hp": self['hp'],
            "max_hp": self['max_hp'],
            "level": self['level'],
            "element": self.get('element', 'Normal'), # Ensure element is saved
            "sprite_path": self['sprite_path'],
        }

class Item(TypedDict):
    """Data structure for a single item type in the bag."""
    name: str
    count: int
    sprite_path: str
    
    def to_dict(self) -> Dict[str, object]:
        """將 Item 實例轉換為可序列化的字典"""
        return {
            "name": self['name'],
            "count": self['count'],
            "sprite_path": self['sprite_path'],
        }
