'''
[TODO HACKATHON 5]
Try to mimic the menu_scene.py or game_scene.py to create this new scene
'''


import pygame as pg

from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from typing import override

class SettingScene(Scene):
    # Background Image
    background: BackgroundSprite
    menu_backgeound: BackgroundSprite
    # Buttons
    back_button: Button
    
    def __init__(self):
        super().__init__() 
        
        font = pg.font.SysFont('inkfree', 30)
        self.text = font.render('Hi Everyone', True, (255, 255, 255))
        self.textrect = self.text.get_rect(center=(GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2))

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
        
        button_size = (50, 50)
        
        normal_img = pg.image.load("assets/images/UI/raw/UI_Flat_IconPlay01a.png").convert_alpha()
        hover_img  = pg.image.load("assets/images/UI/raw/UI_Flat_IconPlay01b.png").convert_alpha()

        # 水平翻轉
        normal_img_flipped = pg.transform.flip(normal_img, True, False)  # True = flip X
        hover_img_flipped  = pg.transform.flip(hover_img, True, False) 

        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4
        self.back_button = Button(
            normal_img_flipped, hover_img_flipped,
            # "UI/raw/UI_Flat_IconPlay01a.png", "UI/raw/UI_Flat_IconPlay01a.png",
            px - 450, py + 20, *button_size,
            lambda: scene_manager.change_scene("menu")
        )
        
        # Text
        def draw_text(text, font, text_col, x, y):
            img = font.render(text, True, text_col)
            
            
        
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg")
        pass

    @override
    def exit(self) -> None:
        pass

    @override
    def update(self, dt: float) -> None:
        if input_manager.key_pressed(pg.K_SPACE):
            scene_manager.change_scene("menu")
            return
        self.back_button.update(dt)

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.menu_backgeound.draw(screen)
        
        # 黑色
        dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        dark_overlay.set_alpha(120)  
        dark_overlay.fill((0, 0, 0))
        screen.blit(dark_overlay, (0, 0))
        
        screen.blit(self.background.image, self.background.rect)
        
        screen.blit(self.text, self.textrect)
        self.back_button.draw(screen)
