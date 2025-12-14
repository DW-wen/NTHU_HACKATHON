from __future__ import annotations
import pygame as pg

from src.utils.definition import Direction
from .entity import Entity
from src.core.services import input_manager
from src.utils import Position, PositionCamera, GameSettings, Logger
from src.core import GameManager
import math
from typing import override

class Player(Entity):
    speed: float = 4.0 * GameSettings.TILE_SIZE
    game_manager: GameManager
    
    is_moving: bool = False
    auto_move_path: list | None = None

    def __init__(self, x: float, y: float, game_manager: GameManager) -> None:
        super().__init__(x, y, game_manager)

    def is_standing_still(self) -> bool:
        """檢查玩家是否處於靜止狀態 (即沒有輸入指令或移動速度為零)。"""
        return not self.is_moving
    
    @override
    def update(self, dt: float) -> None:
        from src.utils import Position
        dis = Position(0, 0)

        # Auto-move override: if a path is set, we drive the player along waypoints
        if getattr(self, 'auto_move_path', None):
            target = self.auto_move_path[0]
            vec_x = target.x - self.position.x
            vec_y = target.y - self.position.y
            dist_to_target = (vec_x ** 2 + vec_y ** 2) ** 0.5
            # consider reached if within movement step or small tolerance
            # use dt-aware threshold if possible; fallback to 2 px
            threshold = max(self.speed * 0.016, 2)  # assume 60fps ~ 16ms for threshold fallback
            if dist_to_target <= threshold:
                # snap exactly to waypoint to avoid offset accumulation
                self.position = type(self.position)(target.x, target.y)
                self.auto_move_path.pop(0)
                if len(self.auto_move_path) == 0:
                    self.auto_move_path = None
                    self.is_moving = False
                else:
                    # still more waypoints; continue next tick
                    self.is_moving = True
                # update animation rect position immediately
                self.animation.update_pos(self.position)
                return

            # set movement direction towards target
            length = dist_to_target
            if length > 0:
                dis.x = (vec_x / length)
                dis.y = (vec_y / length)
        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= 1
            
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += 1
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= 1
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += 1
        
        # Calculate distance
        if dis.x != 0 or dis.y != 0:
            length = dis.distance_to(Position(0, 0))
            dis.x = dis.x / length * self.speed
            dis.y = dis.y / length * self.speed
            
            if abs(dis.x) > abs(dis.y):
                self.direction = Direction.RIGHT if dis.x > 0 else Direction.LEFT
            else:
                self.direction = Direction.DOWN if dis.y > 0 else Direction.UP
            
            self.animation.switch(self.direction.name.lower())
        
        
        dx = dis.x * dt
        dy = dis.y * dt
        
        player_rect = self.animation.rect.copy()
        
        # Move X
        
        player_new_position = Position(self.position.x , self.position.y)
        
        player_rect.x = self.position.x + dx
        player_rect.y = self.position.y
        # if not self.game_manager.check_collision(player_rect):
        #     self.position.x += dx
        if self.game_manager.check_collision(player_rect):
            self.position = Position(self._snap_to_grid(self.position.x), self.position.y)
        else:
            self.position = Position(self.position.x + dx, self.position.y)
        
         # Move Y
        
        player_rect.x = self.position.x
        player_rect.y = self.position.y + dy
        # if not self.game_manager.check_collision(player_rect):
        #     self.position.y += dy
        if self.game_manager.check_collision(player_rect):
            self.position =  Position(self.position.x, self._snap_to_grid(self.position.y))
        else:
            self.position = Position(self.position.x, self.position.y + dy)
        
        # update the rect position
        self.animation.update_pos(self.position) 
        
        # Check teleportation
        tp = self.game_manager.current_map.check_teleport(self.position)
        if tp:
            self.is_teleporting = True
            dest = tp.destination
            self.game_manager.switch_map(dest)
                
        super().update(dt)

    def set_auto_move(self, waypoints: list) -> None:
        """Set a list of Position waypoints (pixel coordinates) for automatic movement."""
        self.auto_move_path = waypoints.copy() if waypoints else None

    def clear_auto_move(self) -> None:
        self.auto_move_path = None

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        
    @override
    def to_dict(self) -> dict[str, object]:
        return super().to_dict()
    
    @classmethod
    @override
    def from_dict(cls, data: dict[str, object], game_manager: GameManager) -> Player:
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, game_manager)

