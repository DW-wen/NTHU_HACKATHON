import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager, scene_manager
from src.sprites import Sprite
from src.interface.components import Button
from src.interface.components.minimap import Minimap
from typing import override

class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite
    
    _enter_delay_timer: float
    _enter_delay_duration: float = 2.0
    
    def __init__(self, game_manager: GameManager):
        super().__init__()
        # Game Manager
        manager = GameManager.load("saves/game0.json")
        if manager is None:
            Logger.error("Failed to load game manager")
            exit(1)
        self.game_manager = game_manager
        
        self._enter_delay_timer = 0.0
        
        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
        else:
            self.online_manager = None
        from src.sprites import Animation
        self.sprite_online = Animation(
            "character/ow1.png", ["down", "left", "right", "up"], 4,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        )
        
        # Button 
        px, py = GameSettings.SCREEN_WIDTH * 7 // 8, GameSettings.SCREEN_HEIGHT  // 7
        self.settiung_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            px + 70, py - 50, 50, 50,
            lambda: scene_manager.change_scene("setting")
        )
        self.backpack_button = Button(
            "UI/button_backpack.png", "UI/button_backpack_hover.png",
            px , py - 50, 50, 50,
            lambda: scene_manager.change_scene("backpack")
        )

        # Minimap (top-left)
        self.minimap = Minimap(self.game_manager, width=200, height=150, pos=(8, 8))
    
    def _get_bush_layer_data(self):
        bush_layer = self.game_manager.current_map.get_layer_by_name("PokemonBush")
        
        # 假設 get_layer_by_name 返回的是一個包含 CSV 數據 (數字陣列) 的物件
        if bush_layer:
            # Tiled map 的 CSV 數據中，非 0 的數字代表有圖塊存在
            # 這裡的數據是 Layer ID，只要 > 0 就表示是草叢
            return bush_layer.data 
        return None
    
    def check_bush_encounter(self) -> bool:
        # 確保玩家存在
        if not self.game_manager.player:
            return False
        
        # 💥 新增：檢查是否按下了空格鍵
        from src.core.services import input_manager
        if not input_manager.key_down(pg.K_SPACE):
            # 如果沒有按下空格鍵，則不觸發戰鬥
            
            return False
        
        # 獲取玩家所在的格子座標 (Tile Position)
        # 💥 修正：將像素座標除以 TILE_SIZE 得到圖塊座標
        player_tile_x = int(self.game_manager.player.position.x // GameSettings.TILE_SIZE)
        player_tile_y = int(self.game_manager.player.position.y // GameSettings.TILE_SIZE)
        
        # 獲取草叢圖層數據
        bush_data = self.game_manager.current_map.get_layer_by_name("PokemonBush")
        
        if bush_data is None:
            return False
          
        # 獲取地圖寬度
        try:
            map_width = self.game_manager.current_map.tmxdata.width
        except AttributeError:
            # 如果 Map 類別的 tmxdata 不存在或沒有 width 屬性，使用硬編碼作為後備
            map_width = 66
            Logger.warning("Using hardcoded map width for bush check.")
                
        # 計算扁平化數組中的索引
        index = player_tile_y * map_width + player_tile_x
        
        # 檢查索引是否在有效範圍內
        if 0 <= index < len(bush_data):
            tile_id = bush_data[index]
            Logger.info(tile_id)
            # 檢查 tile_id 是否為 4
            if tile_id == 81:
                # 玩家在圖塊 ID 4 的草叢上，且按下了空格鍵，立即觸發戰鬥
                Logger.warning("Bush fight")  
                Logger.info("Wild Pokémon encountered (Tile ID 4 hit by SPACE)!")
                # 觸發戰鬥場景
                scene_manager.change_scene("catch")
                
                # 返回 True 表示已觸發事件，並停止當前 update 循環 (在 GameScene.update 中)
                return True
            
        return False
    
    def check_special_map_interaction(self) -> bool:
        # 1. 檢查當前地圖是否為 gym.tmx
        if self.game_manager.current_map_key != "gym.tmx":
            return False

        from src.core.services import input_manager
        
        # 2. 檢查是否按下了互動鍵 (假設購買鍵是 U)
        if not input_manager.key_down(pg.K_u):
            return False
            
        Logger.info("Hi")
            
        return False
    
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        if self.online_manager:
            self.online_manager.enter()
            
        self._enter_delay_timer = self._enter_delay_duration
        
    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()
        
    @override
    def update(self, dt: float):
        
        if self._enter_delay_timer > 0:
            self._enter_delay_timer -= dt
            if self._enter_delay_timer < 0:
                self._enter_delay_timer = 0
        # Check if there is assigned next scene
        self.game_manager.try_switch_map()
        
        # 💥 修正：如果場景正在切換到非 GameScene，則不執行遊戲邏輯
        if scene_manager.next_scene_name and scene_manager.next_scene_name != "game":
            return 
            
        # 💥 修正：如果當前活動場景不是 GameScene，則不執行遊戲邏輯
        if scene_manager.current_scene != self: # 或者用更簡單的方法，如果 scene_manager 知道當前場景類型
            return
        
        from src.core.services import input_manager
        is_space_pressed = input_manager.key_down(pg.K_SPACE)
        # Toggle minimap with M
        
        # 💥 NEW: 如果計時器還在運行，且 SPACE 被按下，我們需要在這裡阻止 SPACE 鍵被 check_bush_encounter 處理
        # 由於 check_bush_encounter 內置了對 SPACE 鍵的檢查，我們需要在呼叫它之前檢查延遲狀態。
        
        # Update player and other data
        if self.game_manager.player:
            self.game_manager.player.update(dt)
            
            if self.check_special_map_interaction():
                return
            
            
            # 💥 NEW: 只有當延遲結束時，才檢查草叢戰鬥遭遇
            if self._enter_delay_timer <= 0:
                if self.check_bush_encounter():
                    return
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)
            
        # Update others
        self.game_manager.bag.update(dt)
        
        if self.game_manager.player is not None and self.online_manager is not None:
            _ = self.online_manager.update(
                self.game_manager.player.position.x, 
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name,
                direction=self.game_manager.player.direction.name.lower(),
                moving=self.game_manager.player.is_moving,
            )
        
        self.settiung_button.update(dt)
        self.backpack_button.update(dt)
        self.minimap.update(dt)
        # advance online sprite animation time
        if self.sprite_online:
            self.sprite_online.update(dt)

    @override
    def draw(self, screen: pg.Surface):          
        if self.game_manager.player:
            
            camera = self.game_manager.player.camera
        else:
            camera = PositionCamera(0, 0)
        
       
            
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)

        self.game_manager.current_map.draw(screen, camera)
        
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)
        
        
        if self.game_manager.player:
             self.game_manager.player.draw(screen, camera)
        
        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                if player["map"] == self.game_manager.current_map.path_name:
                    cam = self.game_manager.player.camera
                    pos = cam.transform_position_as_position(Position(player["x"], player["y"]))
                    # Direction may be 'down','left','right','up'
                    dir_name = str(player.get("dir", "down")).lower()
                    moving = bool(player.get("moving", False))
                    self.sprite_online.switch(dir_name)
                    self.sprite_online.update_pos(pos)
                    # If player not moving, draw static first frame
                    self.sprite_online.draw(screen, static=(not moving))
                    
         # Button
        self.settiung_button.draw(screen)
        
        self.backpack_button.draw(screen)
        # draw minimap on top-left
        self.minimap.draw(screen)
