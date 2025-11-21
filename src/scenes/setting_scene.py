'''
[TODO HACKATHON 5]
Try to mimic the menu_scene.py or game_scene.py to create this new scene
'''


from logging import Logger
import pygame as pg

from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from typing import override
from src.core.managers.game_manager import GameManager

class SettingScene(Scene):
    # Background Image
    background: BackgroundSprite
    menu_backgeound: BackgroundSprite
    # Buttons
    back_button: Button
    
    def __init__(self):
        super().__init__() 
        
        

        self.menu_backgeound = BackgroundSprite("backgrounds/background1.png")
        
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
        self.setting_name_place = pg.Rect(GameSettings.SCREEN_WIDTH // 4 - 150, GameSettings.SCREEN_HEIGHT // 4 - 50, 300, 100)
        
        # Volumne
        font = pg.font.SysFont('inkfree', 30)
        
        self.dragging_volume = False
        self.volume_value = int(GameSettings.AUDIO_VOLUME)  # 初始音量百分比
        
        self.volume_name = font.render(f'Volume: {self.volume_value}%', True, (255, 255, 255))
        self.volume_name_place = pg.Rect(GameSettings.SCREEN_WIDTH // 4 - 150, GameSettings.SCREEN_HEIGHT // 4 + 20, 300, 100)
        
        ## Volume Slider
        self.flat_bar_img = pg.image.load("assets/images/UI/raw/UI_Flat_Bar01a.png")
        self.volume_controller_img = pg.image.load("assets/images/UI/raw/UI_Flat_Handle03a.png")
        self.flat_bar_plc = pg.Rect(GameSettings.SCREEN_WIDTH // 4 - 150, GameSettings.SCREEN_HEIGHT // 4 + 70, GameSettings.SCREEN_HEIGHT * 3 // 4, 30)
        self.volume_controller_plc = pg.Rect(GameSettings.SCREEN_WIDTH // 4 - 150, GameSettings.SCREEN_HEIGHT // 4 + 65, 40, 40)
        self.flat_bar_img = pg.transform.scale(
            self.flat_bar_img,
            (self.flat_bar_plc.width, self.flat_bar_plc.height)
        )
        self.volume_controller_img = pg.transform.scale(
            self.volume_controller_img,
            (self.volume_controller_plc.width, self.volume_controller_plc.height)
        )
   
        # Mute
        font = pg.font.SysFont('inkfree', 30)
        self.mute = "Off"
        self.mute_status =  pg.image.load("assets/images/UI/raw/UI_Flat_FrameSlot01a.png") 
        self.mute_name = font.render(f'Mute: {self.mute}', True, (255, 255, 255))
        self.mute_name_place = pg.Rect(GameSettings.SCREEN_WIDTH // 4 - 150, GameSettings.SCREEN_HEIGHT // 4 + 120, 300, 100)
        self.mute_button = Button(
            self.mute_status, self.mute_status,
            # "UI/raw/UI_Flat_IconPlay01a.png", "UI/raw/UI_Flat_IconPlay01a.png",
            GameSettings.SCREEN_WIDTH // 4 , GameSettings.SCREEN_HEIGHT // 4 + 130, 30, 10,
            self.toggle_mute
        )
        self.mute_button_background = Button(
            "UI/raw/UI_Flat_Bar01a.png", "UI/raw/UI_Flat_Bar01a.png",
           
            GameSettings.SCREEN_WIDTH // 4 -10, GameSettings.SCREEN_HEIGHT // 4 + 120, 50, 30,
        )
        
        # Back Button
        button_size = (50, 50)
        
        normal_img = pg.image.load("assets/images/UI/raw/UI_Flat_IconPlay01a.png").convert_alpha()
        hover_img  = pg.image.load("assets/images/UI/raw/UI_Flat_IconPlay01b.png").convert_alpha()
        normal_img_flipped = pg.transform.flip(normal_img, True, False)  # True = flip X
        hover_img_flipped  = pg.transform.flip(hover_img, True, False) 
        
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4
        self.back_button = Button(
            normal_img_flipped, hover_img_flipped,
            # "UI/raw/UI_Flat_IconPlay01a.png", "UI/raw/UI_Flat_IconPlay01a.png",
            px - 450, py + 20, *button_size,
            lambda: scene_manager.change_scene("menu")
        )
        
        # save and load button
        self.save_img = pg.image.load("assets/images/UI/button_save.png")
        self.save_img_hover = pg.image.load("assets/images/UI/button_save_hover.png")
        self.save_button = Button(
            self.save_img, self.save_img_hover,
            px - 370, py + 20, *button_size,
            lambda: GameManager.save()
        )
        self.load_img = pg.image.load("assets/images/UI/button_load.png")
        self.load_img_hover = pg.image.load("assets/images/UI/button_load_hover.png")
        self.load_button = Button(
            self.load_img, self.load_img_hover,
            px - 290, py + 20, *button_size,
            lambda: GameManager.load()
        )
        
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
        
        
    def toggle_mute(self):
        font = pg.font.SysFont('inkfree', 30)

        if self.mute == "Off":
            self.mute = "On"
            new_img = pg.image.load("assets/images/UI/raw/UI_Flat_Bar10a.png")
            sound_manager.set_bgm_volume(0)

        else:
            self.mute = "Off"
            new_img = pg.image.load("assets/images/UI/raw/UI_Flat_FrameSlot01a.png")
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
        sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg")
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
            
            
        

    @override
    def update(self, dt: float):
       
        if self.dragging_volume and self.mute == "Off":
            mx, my = pg.mouse.get_pos()
            bar_left = self.flat_bar_plc.x
            bar_right = self.flat_bar_plc.x + self.flat_bar_plc.width - self.volume_controller_plc.width

            new_x = mx - self.volume_controller_plc.width // 2
            new_x = max(bar_left, min(bar_right, new_x))
            self.volume_controller_plc.x = new_x

            # 計算音量
            bar_len = bar_right - bar_left
            self.volume_value = int(((new_x - bar_left) / bar_len) * 100)
           

            font = pg.font.SysFont('inkfree', 30)
            self.volume_name = font.render(f'Volume: {self.volume_value}%', True, (255, 255, 255))

            
            sound_manager.set_bgm_volume(self.volume_value / 100)

        self.back_button.update(dt)
        self.mute_button.update(dt)
        self.save_button.update(dt)
        self.load_button.update(dt)
        self.close_button.update(dt)

    @override
    def draw(self, screen: pg.Surface) -> None:
        
        
        # 黑色
        dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        dark_overlay.set_alpha(120)  
        dark_overlay.fill((0, 0, 0))
        screen.blit(dark_overlay, (0, 0))
        
        screen.blit(self.background.image, self.background.rect)
        
        screen.blit(self.setting_name, self.setting_name_place)
        
        screen.blit(self.volume_name, self.volume_name_place)
        screen.blit(self.flat_bar_img, self.flat_bar_plc)
        screen.blit(self.volume_controller_img, self.volume_controller_plc)
        
        
        screen.blit(self.mute_name, self.mute_name_place)
        self.mute_button_background.draw(screen)
        self.mute_button.draw(screen)
        
        self.save_button.draw(screen)
        self.load_button.draw(screen)
        self.back_button.draw(screen)
        self.close_button.draw(screen)
        
