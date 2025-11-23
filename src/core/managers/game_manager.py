from __future__ import annotations
from src.utils import Logger, GameSettings, Position, Teleport
import json, os
import pygame as pg
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from src.maps.map import Map
    from src.entities.player import Player
    from src.entities.enemy_trainer import EnemyTrainer
    from src.data.bag import Bag

class GameManager:
    # Entities
    player: Player | None
    enemy_trainers: dict[str, list[EnemyTrainer]]
    bag: "Bag"
    
    # Map properties
    current_map_key: str
    maps: dict[str, Map]
    
    # Changing Scene properties
    should_change_scene: bool
    next_map: str
    is_teleporting: bool # 屬性已在 __init__ 中定義
    
    def __init__(self, maps: dict[str, Map], start_map: str, 
                 player: Player | None,
                 enemy_trainers: dict[str, list[EnemyTrainer]], 
                 bag: Bag | None = None):
                         
        from src.data.bag import Bag
        # Game Properties
        self.maps = maps
        self.current_map_key = start_map
        self.player = player
        self.enemy_trainers = enemy_trainers
        self.bag = bag if bag is not None else Bag([], [])
        
        # Check If you should change scene
        self.should_change_scene = False
        self.next_map = ""
        self.is_teleporting = False
        
    @property
    def current_map(self) -> Map:
        return self.maps[self.current_map_key]
        
    @property
    def current_enemy_trainers(self) -> list[EnemyTrainer]:
        return self.enemy_trainers[self.current_map_key]
        
    @property
    def current_teleporter(self) -> list[Teleport]:
        return self.maps[self.current_map_key].teleporters
    
    def switch_map(self, target: str) -> None:
        if target not in self.maps:
            Logger.warning(f"Map '{target}' not loaded; cannot switch.")
            return
        
        self.next_map = target
        self.should_change_scene = True
            
    def try_switch_map(self) -> None:
        if self.should_change_scene:
            self.current_map_key = self.next_map
            self.next_map = ""
            self.should_change_scene = False
            if self.player:
                # 傳送時，玩家會被移動到新地圖的重生點 (spawn)
                self.player.position = self.maps[self.current_map_key].spawn
            self.is_teleporting = False
            
    def check_collision(self, rect: pg.Rect) -> bool:
        if self.maps[self.current_map_key].check_collision(rect):
            return True
        for entity in self.enemy_trainers[self.current_map_key]:
            # 檢查敵方訓練師碰撞
            if rect.colliderect(entity.animation.rect):
                return True
        
        return False
        
    def save(self, path: str) -> None:
        try:
            # 確保 saves 目錄存在
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            Logger.info(f"Game saved to {path}")
        except Exception as e:
            Logger.warning(f"Failed to save game: {e}")
            
    @classmethod
    def load(cls, path: str) -> "GameManager | None":
        if not os.path.exists(path):
            Logger.error(f"No file found: {path}, ignoring load function")
            return None

        try:
            with open(path, "r") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            Logger.error(f"Failed to load game: Invalid JSON file at {path}. Error: {e}")
            return None
        except Exception as e:
             Logger.error(f"An unexpected error occurred during load: {e}")
             return None

    def to_dict(self) -> dict[str, object]:
        """
        將 GameManager 的所有狀態序列化為字典。
        --- 修正: 移除 player_spawns 的錯誤邏輯 ---
        """
        map_blocks: list[dict[str, object]] = []
        for key, m in self.maps.items():
            # 1. 儲存地圖本身資料
            block = m.to_dict()
            
            # 2. 儲存該地圖上的敵方訓練師狀態
            block["enemy_trainers"] = [t.to_dict() for t in self.enemy_trainers.get(key, [])]
            
            # **移除舊的 player_spawns 邏輯**
            # 儲存地圖時不需要將玩家的位置塞入每個地圖的區塊中。
            # 玩家的當前位置只需在頂層的 "player" 區塊中儲存一次。
            
            map_blocks.append(block)

        # 頂層儲存 Player 的所有狀態 (包括其當前的位置和地圖)
        player_dict = None
        if self.player is not None:
            # Player.to_dict 應該儲存 Player 的所有細節，包括當前在地圖上的精確位置 (x, y)。
            player_dict = self.player.to_dict()
            # 額外將 player 正在的地圖資訊存入，以確認載入後位置的有效性。
            player_dict["current_map_key"] = self.current_map_key
            
        return {
            "map": map_blocks,
            "current_map": self.current_map_key,
            "player": player_dict,
            "bag": self.bag.to_dict(),
        } 

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "GameManager":
        from src.maps.map import Map
        from src.entities.player import Player
        from src.entities.enemy_trainer import EnemyTrainer
        from src.data.bag import Bag
        
        # 為了類型提示，將 dict[str, object] 轉換為更具體的類型
        data = cast(dict, data) 
        
        Logger.info("Loading maps")
        maps_data = data["map"]
        maps: dict[str, Map] = {}
        trainers: dict[str, list[EnemyTrainer]] = {} # 初始化訓練師字典

        # 1. 載入地圖和地圖上的靜態資料 (重生點、傳送點、碰撞層等)
        for entry in maps_data:
            path = entry["path"]
            maps[path] = Map.from_dict(entry)
        
        current_map_key = data["current_map"]
        
        # 2. 初始化 GameManager (此時 Player 和 Trainer 暫時為 None/空)
        gm = cls(
            maps, current_map_key,
            None, # Player 稍後載入
            trainers, # Trainers 稍後載入
            bag=None # Bag 稍後載入
        )
        
        # 3. 載入敵方訓練師狀態 (需在 Map 載入後進行，因為 Trainer 依賴 Map 數據)
        Logger.info("Loading enemy trainers")
        for m in data["map"]:
            raw_data = m.get("enemy_trainers", [])
            # 確保 Trainer 載入時能夠取得 GameManager 實例
            gm.enemy_trainers[m["path"]] = [EnemyTrainer.from_dict(t, gm) for t in raw_data]
        
        # 4. 載入 Player 狀態 (Player 載入時也需要 GameManager 實例)
        Logger.info("Loading Player")
        if data.get("player"):
            player_data = data["player"]
            gm.player = Player.from_dict(player_data, gm)
            
            # 確保玩家被放置在正確的地圖 (但 switch_map 的邏輯會將玩家移動到地圖重生點)
            # 在 Player.from_dict 中，應該已經根據 player_data 中的 x, y 設置了位置。
            if player_data.get("current_map_key") and player_data["current_map_key"] != current_map_key:
                 Logger.warning(f"Player data map key mismatch. Player position loaded for {current_map_key}.")

        # 5. 載入 Bag
        Logger.info("Loading bag")
        from src.data.bag import Bag as _Bag
        # 使用 .get("bag", {}) 以避免 key 錯誤
        gm.bag = Bag.from_dict(data.get("bag", {})) 

        return gm