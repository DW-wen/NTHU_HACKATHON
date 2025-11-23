import pygame as pg

from src.core.managers.game_manager import GameManager
from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from typing import override

class BackpackScene(Scene):
    # Background Image
    background: BackgroundSprite
    # Buttons
    play_button: Button
    setting_button: Button
    
    def __init__(self, game_manager: GameManager):
        super().__init__()
        
        self.game_manager = game_manager
        self.pokemon_displays = []
        self.item_displays = []
        
        # 初始化時先呼叫一次建立列表
        self._initialize_displays()
        
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
        
    def _initialize_displays(self):
        """用於初始化或重新初始化 Pokémon 和 Item 顯示列表的輔助方法。"""
        # 清空現有的顯示列表
        self.pokemon_displays.clear()
        self.item_displays.clear()
        
        # ======================================================================
        # Pokémon LIST（左側）
        # ======================================================================
        base_x = GameSettings.SCREEN_WIDTH // 5 - 70
        base_y = GameSettings.SCREEN_HEIGHT // 5
        spacing = 100

        for i, mon in enumerate(self.game_manager.bag._monsters_data):
            self.pokemon_displays.append(
                PokemonDisplay(
                    sprite_path=f"assets/images/{mon['sprite_path']}",
                    x=base_x,
                    y=base_y + i * spacing,
                    hp_current=mon["hp"],
                    hp_max=mon["max_hp"],
                    level=mon["level"]
                )
            )

        # ======================================================================
        # ITEMS LIST（右側）
        # ======================================================================
        base_x_items = GameSettings.SCREEN_WIDTH * 2 // 3 - 90
        base_y_items = GameSettings.SCREEN_HEIGHT // 4
        spacing_items = 80

        for i, item in enumerate(self.game_manager.bag._items_data):
            self.item_displays.append(
                ItemDisplay(
                    name=item["name"],
                    image_path=f"assets/images/{item['sprite_path']}",
                    x=base_x_items,
                    y=base_y_items + i * spacing_items,
                    quantity=item["count"]
                )
            )
        
        # close_button
        close_px = GameSettings.SCREEN_WIDTH * 3 // 4 + 90
        close_py = GameSettings.SCREEN_HEIGHT // 4 - 60
        self.close_img = pg.image.load("assets/images/UI/button_x.png")
        self.close_img_hover = pg.image.load("assets/images/UI/button_x_hover.png")
        self.close_button = Button(
            self.close_img, self.close_img_hover,
            close_px , close_py , 50, 50,
            lambda: scene_manager.close_overlay()
        )
           
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg")
        self._initialize_displays()
        pass

    @override
    def exit(self) -> None:
        pass

    @override
    def update(self, dt: float) -> None:
        self.close_button.update(dt)
        pass

    @override
    def draw(self, screen: pg.Surface) -> None:
        
        # Black 
        dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        dark_overlay.set_alpha(120)  
        dark_overlay.fill((0, 0, 0))
        screen.blit(dark_overlay, (0, 0))
        
        screen.blit(self.background.image, self.background.rect)
        
        # Pokémon list
        for p in self.pokemon_displays:
            p.draw(screen)

        # Items list
        for it in self.item_displays:
            it.draw(screen)
        
        self.close_button.draw(screen)

        
class ItemDisplay:
    def __init__(self, name: str, image_path: str, x: int, y: int, quantity: int = 0):
        """
        name: 顯示的名字（ex: Potion）
        image_path: 圖片路徑
        x, y: icon 左上角座標
        quantity: 數量
        """
        self.name = name
        self.quantity = quantity

        # Icon Rect (固定 50x50，或你可改大小)
        self.icon_rect = pg.Rect(x, y, 50, 50)

        # Load & scale image
        self.icon = pg.image.load(image_path)
        self.icon = pg.transform.scale(self.icon, (50, 50))

        # Font
        self.font = pg.font.SysFont("inkfree", 30)

        # Text positions
        self.name_rect = pg.Rect(x + 60, y + 10, 200, 50)
        self.number_rect = pg.Rect(x + 180, y + 10, 100, 50)

        self.update_text()

    def update_text(self):
        """重新產生文字（例如更新數量時）"""
        self.name_surface = self.font.render(self.name, True, (255, 255, 255))
        self.number_surface = self.font.render(str(self.quantity), True, (255, 255, 255))

    def set_quantity(self, value: int):
        """更新數量"""
        self.quantity = value
        self.update_text()

    def draw(self, screen: pg.Surface):
        """畫出 Item Display"""
        screen.blit(self.icon, self.icon_rect)
        screen.blit(self.name_surface, self.name_rect)
        screen.blit(self.number_surface, self.number_rect)

class PokemonDisplay:
    def __init__(self, sprite_path: str, x: int, y: int,
                 hp_current: int, hp_max: int, level: int):

        self.x = x
        self.y = y

        # --- Background ---
        self.bg = pg.image.load("assets/images/UI/raw/UI_Flat_Banner03a.png")
        self.bg = pg.transform.scale(self.bg, (500, 80))
        self.bg_rect = pg.Rect(x, y, 500, 80)

        # --- Pokémon Sprite ---
        self.sprite = pg.image.load(sprite_path)
        self.sprite = pg.transform.scale(self.sprite, (70, 70))
        self.sprite_rect = pg.Rect(x + 30, y - 10, 70, 70)

        # --- Stats ---
        self.font = pg.font.SysFont("inkfree", 30)

        self.hp_current = hp_current
        self.hp_max = hp_max
        self.level = level

        self.update_text()

    def update_text(self):
        """重新產生文字（HP、LV）"""
        self.hp_surface = self.font.render(
            f"HP: {self.hp_current} / {self.hp_max}", True, (0, 0, 0)
        )
        self.hp_rect = pg.Rect(self.x + 110, self.y + 20, 200, 50)

        self.level_surface = self.font.render(
            f"LV: {self.level}", True, (0, 0, 0)
        )
        self.level_rect = pg.Rect(self.x + 350, self.y + 25, 200, 50)

    def set_hp(self, current: int, max_hp: int | None = None):
        """更新 HP"""
        self.hp_current = current
        if max_hp is not None:
            self.hp_max = max_hp
        self.update_text()

    def set_level(self, level: int):
        """更新等級"""
        self.level = level
        self.update_text()

    def draw(self, screen: pg.Surface):
        """畫出完整 Pokémon 區塊"""
        screen.blit(self.bg, self.bg_rect)
        screen.blit(self.sprite, self.sprite_rect)
        screen.blit(self.hp_surface, self.hp_rect)
        screen.blit(self.level_surface, self.level_rect)