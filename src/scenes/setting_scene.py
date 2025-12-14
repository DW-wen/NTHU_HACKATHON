# src/scenes/setting_scene.py (Mimic file content)

from logging import Logger
import pygame as pg

from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from typing import override
# 確保這個導入是正確的
from src.core.managers.game_manager import GameManager 


class SettingScene(Scene):
    # Background Image
    background: BackgroundSprite
    # Buttons
    back_button: Button
    # 新增 GameManager 屬性
    game_manager: GameManager 
    
    def __init__(self, game_manager: GameManager): # 接受 GameManager
        super().__init__() 
        self.game_manager = game_manager # 儲存 GameManager
        
        # ... (其它初始化不變)

        self.background = BackgroundSprite("UI/raw/UI_Flat_Frame03a.png") 
        # 讓背景圖片縮小成螢幕大小的 80%
        bg_scale = 0.8
        bg_size = (
            int(GameSettings.SCREEN_WIDTH * bg_scale),
            int(GameSettings.SCREEN_HEIGHT * bg_scale)
        )
        # 將背景縮放並置中
        self.background.image = pg.transform.scale(self.background.image, bg_size)
        self.background.rect = self.background.image.get_rect(
            center=(GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2)
        )
        # Text
        # Setting
        font = pg.font.SysFont('inkfree', 50)
        self.setting_name = font.render('Setting', True, (255, 255, 255))
        # 修正 place 的位置以確保置中在背景框架內
        self.setting_name_place = self.setting_name.get_rect(
            centerx=GameSettings.SCREEN_WIDTH // 2, 
            y=GameSettings.SCREEN_HEIGHT // 4 - 50
        )
        
        # Volumne
        font = pg.font.SysFont('inkfree', 30)
        
        self.dragging_volume = False
        # 初始音量從 GameSettings 取得，並確保是百分比 (0-100)
        self.volume_value = int(GameSettings.AUDIO_VOLUME * 100) 
        
        self.volume_name = font.render(f'Volume: {self.volume_value}%', True, (255, 255, 255))
        self.volume_name_place = pg.Rect(GameSettings.SCREEN_WIDTH // 4 - 150, GameSettings.SCREEN_HEIGHT // 4 + 20, 300, 100)
        
        ## Volume Slider
        self.flat_bar_img = pg.image.load("assets/images/UI/raw/UI_Flat_Bar01a.png")
        self.volume_controller_img = pg.image.load("assets/images/UI/raw/UI_Flat_Handle03a.png")
        # 條狀圖的位置和尺寸
        self.flat_bar_plc = pg.Rect(GameSettings.SCREEN_WIDTH // 4 + 10, GameSettings.SCREEN_HEIGHT // 4 + 70, 
                                   GameSettings.SCREEN_WIDTH * 3 // 8, 30) # 修正寬度比例
        # 控制器圖片的尺寸
        controller_size = 40
        
        # 控制器的初始 X 座標計算: 必須基於初始音量百分比 (self.volume_value)
        bar_left = self.flat_bar_plc.x
        bar_right = self.flat_bar_plc.x + self.flat_bar_plc.width - controller_size
        bar_len = bar_right - bar_left
        initial_controller_x = bar_left + int(bar_len * (self.volume_value / 100))
        
        # 控制器圖片的位置
        self.volume_controller_plc = pg.Rect(initial_controller_x, 
                                             self.flat_bar_plc.centery - controller_size // 2, 
                                             controller_size, controller_size)
        
        self.flat_bar_img = pg.transform.scale(
            self.flat_bar_img,
            (self.flat_bar_plc.width, self.flat_bar_plc.height)
        )
        self.volume_controller_img = pg.transform.scale(
            self.volume_controller_img,
            (self.volume_controller_plc.width, self.volume_controller_plc.height)
        )
        
        # Mute (不變)
        # ... (Mute 相關的初始化程式碼)
        
        # Mute
        font = pg.font.SysFont('inkfree', 30)
        # 初始設定為 Off，但應與 GameSettings.AUDIO_VOLUME 檢查
        self.mute = "On" if GameSettings.AUDIO_VOLUME == 0 else "Off"
        
        self.mute_status = pg.image.load("assets/images/UI/raw/UI_Flat_FrameSlot01a.png") 
        # 根據初始 mute 狀態載入正確的圖片
        initial_mute_img_path = "assets/images/UI/raw/UI_Flat_Bar10a.png" if self.mute == "On" else "assets/images/UI/raw/UI_Flat_FrameSlot01a.png"
        initial_mute_img = pg.image.load(initial_mute_img_path)
        
        self.mute_name = font.render(f'Mute: {self.mute}', True, (255, 255, 255))
        self.mute_name_place = pg.Rect(GameSettings.SCREEN_WIDTH // 4 - 150, GameSettings.SCREEN_HEIGHT // 4 + 120, 300, 100)
        self.mute_button = Button(
            initial_mute_img, initial_mute_img,
            GameSettings.SCREEN_WIDTH // 4 , GameSettings.SCREEN_HEIGHT // 4 + 130, 30, 10,
            self.toggle_mute
        )
        self.mute_button_background = Button(
            "UI/raw/UI_Flat_Bar01a.png", "UI/raw/UI_Flat_Bar01a.png",
            GameSettings.SCREEN_WIDTH // 4 -10, GameSettings.SCREEN_HEIGHT // 4 + 120, 50, 30,
        )
        
        # Back Button (不變)
        # ... (Back Button 相關的初始化程式碼)

        # Back Button
        button_size = (50, 50)
        
        normal_img = pg.image.load("assets/images/UI/raw/UI_Flat_IconPlay01a.png").convert_alpha()
        hover_img  = pg.image.load("assets/images/UI/raw/UI_Flat_IconPlay01b.png").convert_alpha()
        normal_img_flipped = pg.transform.flip(normal_img, True, False)  # True = flip X
        hover_img_flipped  = pg.transform.flip(hover_img, True, False) 
        
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4
        # Store as instance attributes so other methods can access them (e.g., draw)
        self.px, self.py = px, py
        self.back_button = Button(
            normal_img_flipped, hover_img_flipped,
            # "UI/raw/UI_Flat_IconPlay01a.png", "UI/raw/UI_Flat_IconPlay01a.png",
            px - 450, py + 20, *button_size,
            lambda: scene_manager.change_scene("menu")
        )

        SAVE_PATH = "saves/game0.json" # 修正路徑為更具體的檔案名
        # save and load button
        self.save_img = pg.image.load("assets/images/UI/button_save.png")
        self.save_img_hover = pg.image.load("assets/images/UI/button_save_hover.png")
        self.save_button = Button(
            self.save_img, self.save_img_hover,
            px - 370, py + 20, *button_size,
            # (0.5) Call the save method on the GameManager
            lambda: self.game_manager.save(SAVE_PATH) 
        )
        self.load_img = pg.image.load("assets/images/UI/button_load.png")
        self.load_img_hover = pg.image.load("assets/images/UI/button_load_hover.png")
        self.load_button = Button(
            self.load_img, self.load_img_hover,
            px - 290, py + 20, *button_size,
            # (0.5) Call the handle_load method
            lambda: self.handle_load(SAVE_PATH)
        )

        # Navigation button: auto-move to specified map coordinate
        # Using save button img assets for icon consistency
        self.nav_img = pg.image.load("assets/images/ingame_ui/baricon1.png")
        self.nav_img_hover = pg.image.load("assets/images/ingame_ui/baricon1.png")
        self.nav_button = Button(
            self.nav_img, self.nav_img_hover,
            px - 210, py + 20, *button_size,
            lambda: self.handle_navigate()
        )
        self.nav_status_font = pg.font.SysFont('inkfree', 24)
        self.nav_status_text = self.nav_status_font.render('', True, (255,255,255))
        
        # close button
        # ... (Close Button 相關的初始化程式碼)

        # close button
        close_px = GameSettings.SCREEN_WIDTH * 3 // 4 + 90
        close_py = GameSettings.SCREEN_HEIGHT // 4 - 60
        self.close_img = pg.image.load("assets/images/UI/button_x.png")
        self.close_img_hover = pg.image.load("assets/images/UI/button_x_hover.png")
        self.close_button = Button(
            self.close_img, self.close_img_hover,
            close_px , close_py , *button_size,
            lambda: scene_manager.close_overlay()
        )
        
    def handle_load(self, path: str):
        """處理載入遊戲的邏輯，並在成功時切換場景。"""
        # (0.5) Call the load method on the GameManager
        new_gm = GameManager.load(path)
        
        if new_gm is not None:
            # 成功載入後，更新當前的 GameManager 實例
            # 這是必要的步驟，因為載入會創建一個新的 GameManager 實例
            self.game_manager.maps = new_gm.maps
            self.game_manager.current_map_key = new_gm.current_map_key
            self.game_manager.player = new_gm.player
            self.game_manager.enemy_trainers = new_gm.enemy_trainers
            self.game_manager.bag = new_gm.bag
            
           
            scene_manager.close_overlay()
            self.game_manager.switch_map(self.game_manager.current_map_key)
            pass
        else:
            # 載入失敗的處理 (例如顯示一個錯誤訊息)
            Logger.error("Game load failed.")

    def toggle_mute(self):
        # ... (toggle_mute 程式碼不變)

        font = pg.font.SysFont('inkfree', 30)

        if self.mute == "Off":
            self.mute = "On"
            new_img = pg.image.load("assets/images/UI/raw/UI_Flat_Bar10a.png")
            # 在靜音時，音量設定為 0
            sound_manager.set_bgm_volume(0) 

        else:
            self.mute = "Off"
            new_img = pg.image.load("assets/images/UI/raw/UI_Flat_FrameSlot01a.png")
            # 恢復為音量條的值
            sound_manager.set_bgm_volume(self.volume_value / 100) 

        # 更新文字
        self.mute_name = font.render(f'Mute: {self.mute}', True, (255, 255, 255))

        # 🔥 重新建立按鈕（確保圖片更新）
        self.mute_button = Button(
            new_img, new_img,
            GameSettings.SCREEN_WIDTH // 4,
            GameSettings.SCREEN_HEIGHT // 4 + 130,
            30, 10,
            self.toggle_mute
        )
    
    @override
    def enter(self) -> None:
        # 由於 SettingScene 通常是作為 overlay 在 GameScene 上方，
        # 除非它是 MenuScene 的一部分，否則通常不應在這裡播放新的 BGM。
        # 假設 SettingScene 是從 MenuScene 或 GameScene 進入的。
        # 這裡的 BGM 播放邏輯保留，但可能需要依賴你的遊戲流程進行調整。
        # sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg") 
        pass

    @override
    def exit(self) -> None:
        pass
    
    @override
    def handle_event(self, event):
        # drag the mouse
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.volume_controller_plc.collidepoint(event.pos):
                self.dragging_volume = True

        if event.type == pg.MOUSEBUTTONUP:
            self.dragging_volume = False
        
        # 處理按鈕事件 (由按鈕的 update 方法處理)

    @override
    def update(self, dt: float):
        
        if self.dragging_volume and self.mute == "Off":
            mx, my = pg.mouse.get_pos()
            bar_left = self.flat_bar_plc.x
            # 修正: 確保控制器不會超出滑動條的右側邊界
            bar_right = self.flat_bar_plc.x + self.flat_bar_plc.width - self.volume_controller_plc.width 

            # 將控制器圖片的中心點的 X 座標跟隨滑鼠 X 座標
            new_x = mx - self.volume_controller_plc.width // 2
            # 限制 new_x 在滑動條範圍內
            new_x = max(bar_left, min(bar_right, new_x)) 
            self.volume_controller_plc.x = new_x

            # 計算音量 (使用浮點數除法)
            bar_len = bar_right - bar_left
            # 避免除以零，如果 bar_len 為 0 (不應發生) 則音量為 0
            if bar_len > 0:
                # 換算為 0-100 的百分比
                volume_percentage = ((new_x - bar_left) / bar_len) * 100
                self.volume_value = int(volume_percentage)
            else:
                self.volume_value = 0
            
            font = pg.font.SysFont('inkfree', 30)
            self.volume_name = font.render(f'Volume: {self.volume_value}%', True, (255, 255, 255))

            # 設置音量 (0.0 - 1.0)
            GameSettings.AUDIO_VOLUME = self.volume_value / 100 
            sound_manager.set_bgm_volume(GameSettings.AUDIO_VOLUME)

        self.back_button.update(dt)
        self.mute_button.update(dt)
        self.save_button.update(dt)
        self.load_button.update(dt)
        self.close_button.update(dt)
        self.nav_button.update(dt)

    @override
    def draw(self, screen: pg.Surface) -> None:
        # ... (draw 程式碼不變)
        
        # 黑色
        dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        dark_overlay.set_alpha(120)  
        dark_overlay.fill((0, 0, 0))
        screen.blit(dark_overlay, (0, 0))
        
        screen.blit(self.background.image, self.background.rect)
        
        # 確保文字正確渲染
        self.setting_name = pg.font.SysFont('inkfree', 50).render('Setting', True, (255, 255, 255))
        self.setting_name_place = self.setting_name.get_rect(
            centerx=GameSettings.SCREEN_WIDTH // 2, 
            y=GameSettings.SCREEN_HEIGHT // 4 - 50
        )
        
        screen.blit(self.setting_name, self.setting_name_place)
        
        screen.blit(self.volume_name, self.volume_name_place)
        screen.blit(self.flat_bar_img, self.flat_bar_plc)
        screen.blit(self.volume_controller_img, self.volume_controller_plc)
        
        
        screen.blit(self.mute_name, self.mute_name_place)
        self.mute_button_background.draw(screen)
        self.mute_button.draw(screen)
        
        self.save_button.draw(screen)
        self.load_button.draw(screen)
        self.nav_button.draw(screen)
        
        self.back_button.draw(screen)
        self.close_button.draw(screen)

    def handle_navigate(self):
        """Triggered by nav button: start auto-moving player to map.tmx {x:16,y:30}."""
        # NOTE: target map/key assumed to be "map.tmx", if different, you may need to switch maps first
        target_map = "map.tmx"
        target_tile = (16, 30)
        # If player is on a different map, switch map first then set auto-move after switching
        if self.game_manager.current_map_key != target_map:
            # schedule switch and then auto-move on next tick by setting player position to spawn and returning
            self.game_manager.switch_map(target_map)
            # after switch, auto move will be attempted in enter or update; for simplicity, set nav_status
            self.nav_status_text = self.nav_status_font.render('Switched map. Press nav again.', True, (255,255,255))
            return

        ok = self.game_manager.auto_move_player_to(*target_tile)
        