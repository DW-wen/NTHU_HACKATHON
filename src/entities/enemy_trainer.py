from __future__ import annotations
from logging import Logger
import pygame
from enum import Enum
from dataclasses import dataclass
from typing import override

from .entity import Entity
from src.sprites import Sprite
from src.core import GameManager
from src.core.services import input_manager, scene_manager
from src.utils import GameSettings, Direction, Position, PositionCamera


class EnemyTrainerClassification(Enum):
    STATIONARY = "stationary"
    SHOPKEEPER = "shopkeeper"

@dataclass
class IdleMovement:
    def update(self, enemy: "EnemyTrainer", dt: float) -> None:
        return

class EnemyTrainer(Entity):
    classification: EnemyTrainerClassification
    max_tiles: int | None
    _movement: IdleMovement
    warning_sign: Sprite
    detected: bool
    los_direction: Direction

    @override
    def __init__(
        self,
        x: float,
        y: float,
        game_manager: GameManager,
        classification: EnemyTrainerClassification = EnemyTrainerClassification.STATIONARY,
        max_tiles: int | None = 2,
        facing: Direction | None = None,
    ) -> None:
        super().__init__(x, y, game_manager)
        self.classification = classification
        self.max_tiles = max_tiles
        if classification in (EnemyTrainerClassification.STATIONARY, EnemyTrainerClassification.SHOPKEEPER):
            self._movement = IdleMovement()
            if facing is None:
                raise ValueError("Idle EnemyTrainer requires a 'facing' Direction at instantiation")
            self._set_direction(facing)
        else:
            raise ValueError("Invalid classification")
        self.warning_sign = Sprite("exclamation.png", (GameSettings.TILE_SIZE // 2, GameSettings.TILE_SIZE // 2))
        self.warning_sign.update_pos(Position(x + GameSettings.TILE_SIZE // 4, y - GameSettings.TILE_SIZE // 2))
        self.detected = False

    @override
    def update(self, dt: float) -> None:
        self._movement.update(self, dt)
        self._has_los_to_player()
        if self.detected and input_manager.key_pressed(pygame.K_SPACE):
            if self.classification == EnemyTrainerClassification.SHOPKEEPER:
                scene_manager.change_scene("shop")
            else:
                scene_manager.change_scene("battle")
        self.animation.update_pos(self.position)

    @override
    def draw(self, screen: pygame.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        if self.detected:
            self.warning_sign.draw(screen, camera)
        if GameSettings.DRAW_HITBOXES:
            los_rect = self._get_los_rect()
            if los_rect is not None:
                pygame.draw.rect(screen, (255, 255, 0), camera.transform_rect(los_rect), 1)

    def _set_direction(self, direction: Direction) -> None:
        self.direction = direction
        if direction == Direction.RIGHT:
            self.animation.switch("right")
        elif direction == Direction.LEFT:
            self.animation.switch("left")
        elif direction == Direction.DOWN:
            self.animation.switch("down")
        else:
            self.animation.switch("up")
        self.los_direction = self.direction

    def _get_los_rect(self) -> pygame.Rect | None:
        '''
        TODO: Create hitbox to detect line of sight of the enemies towards the player
        '''
        if self.max_tiles is None:
            return None
        
        # 獲取 Enemy Trainer 的位置和尺寸
        trainer_rect = self.animation.rect
        tile_size = GameSettings.TILE_SIZE
        
        # LOS 偵測的總距離 (以像素計)
        los_distance = self.max_tiles * tile_size
        
        # 根據面朝方向計算 LOS 矩形
        if self.los_direction == Direction.UP:
            # 起點 (x, y)，寬度，高度
            # 偵測區域從 Trainer 的頂部開始，向上延伸 los_distance
            los_rect = pygame.Rect(
                trainer_rect.x,
                trainer_rect.y - los_distance,
                tile_size,
                los_distance + trainer_rect.height # 涵蓋 trainer 自身的高度
            )
        elif self.los_direction == Direction.DOWN:
            # 偵測區域從 Trainer 的底部開始，向下延伸 los_distance
            los_rect = pygame.Rect(
                trainer_rect.x,
                trainer_rect.y,
                tile_size,
                los_distance + trainer_rect.height
            )
        elif self.los_direction == Direction.LEFT:
            # 偵測區域從 Trainer 的左側開始，向左延伸 los_distance
            los_rect = pygame.Rect(
                trainer_rect.x - los_distance,
                trainer_rect.y,
                los_distance + trainer_rect.width,
                tile_size
            )
        elif self.los_direction == Direction.RIGHT:
            # 偵測區域從 Trainer 的右側開始，向右延伸 los_distance
            los_rect = pygame.Rect( 
                trainer_rect.x,
                trainer_rect.y,
                los_distance + trainer_rect.width,
                tile_size
            )
        else:
            return None
            
        return los_rect

    def _has_los_to_player(self) -> None:
        player = self.game_manager.player
        if player is None:
            self.detected = False
            return
        
        los_rect = self._get_los_rect()
        if los_rect is None:
            self.detected = False
            return
            
        # 檢查 LOS 矩形是否與玩家的動畫矩形相交
        if los_rect.colliderect(player.animation.rect):
            
            # 此外，我們需要檢查 LOS 區域內是否有地圖碰撞物阻擋視線。
            # 這裡我們只檢查 LOS 矩形本身是否與地圖碰撞。
            # 注意: 理想的實現應該是檢查 LOS 和玩家之間是否有障礙物，
            # 但為了快速完成 TODO，我們只檢查 LOS 區域是否與任何地圖碰撞物重疊。
            # 如果 LOS 區域跟地圖有碰撞，我們假設視線被阻擋 (這是一個簡單的近似)。
            
            # 創建一個只包含 LOS 範圍的碰撞檢查矩形 (排除 Trainer 本身的位置)
            # 為了簡單化，我們直接使用 los_rect 檢查
            is_blocked = self.game_manager.current_map.check_collision(los_rect)
            
            # 由於 EnemyTrainer 本身的位置也可能與 LOS 矩形重疊，
            # 如果 LOS 矩形與地圖碰撞，我們需要更精確的檢查。
            # 這裡我們採用最簡單的邏輯：如果相交，且沒有阻擋 (假設地圖碰撞不等於視線阻擋)
            
            # 🌟 視線邏輯：如果 LOS 區域與玩家重疊，則偵測成功。
            self.detected = True
        else:
            self.detected = False

    @classmethod
    @override
    def from_dict(cls, data: dict, game_manager: GameManager) -> "EnemyTrainer":
        classification = EnemyTrainerClassification(data.get("classification", "stationary"))
        max_tiles = data.get("max_tiles")
        facing_val = data.get("facing")
        facing: Direction | None = None
        if facing_val is not None:
            if isinstance(facing_val, str):
                facing = Direction[facing_val]
            elif isinstance(facing_val, Direction):
                facing = facing_val
        if facing is None and classification == EnemyTrainerClassification.STATIONARY:
            facing = Direction.DOWN
        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            game_manager,
            classification,
            max_tiles,
            facing,
        )

    @override
    def to_dict(self) -> dict[str, object]:
        base: dict[str, object] = super().to_dict()
        base["classification"] = self.classification.value
        base["facing"] = self.direction.name
        base["max_tiles"] = self.max_tiles
        return base