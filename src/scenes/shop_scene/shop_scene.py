import pygame as pg
from src.scenes.scene import Scene
from src.core.managers.game_manager import GameManager
from src.core.services import scene_manager
from src.scenes.shop_scene.backpack_item import BackpackItem
from src.scenes.shop_scene.shop_item import ShopItem
from src.sprites import BackgroundSprite
from src.interface.components import Button
from src.utils import GameSettings
from typing import override

class ShopScene(Scene):
    def __init__(self, game_manager: GameManager):
        super().__init__()
        self.game_manager = game_manager
        
        # --- UI 背景 ---
        self.background = BackgroundSprite("UI/raw/UI_Flat_Frame03a.png")
        bg_scale = 0.8
        bg_size = (int(GameSettings.SCREEN_WIDTH * bg_scale), int(GameSettings.SCREEN_HEIGHT * bg_scale))
        self.background.image = pg.transform.scale(self.background.image, bg_size)
        self.background.rect = self.background.image.get_rect(center=(GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2))

        # --- 關閉按鈕 ---
        self.close_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            GameSettings.SCREEN_WIDTH * 3 // 4 + 90,
            GameSettings.SCREEN_HEIGHT // 4 - 60,
            50, 50,
            lambda: scene_manager.close_overlay()
        )

        # --- 輔助函數: 創建 +/- 圖標表面 ---
        icon_size = (50, 50)
        def make_icon(char: str, bg_color, fg_color):
            surf = pg.Surface(icon_size, pg.SRCALPHA)
            surf.fill((0, 0, 0, 0))
            pg.draw.ellipse(surf, bg_color, (0, 0, icon_size[0], icon_size[1]))
            cx, cy = icon_size[0] // 2, icon_size[1] // 2
            thick = 6
            if char == "+":
                pg.draw.rect(surf, fg_color, (cx - thick // 2, 10, thick, icon_size[1] - 20))
                pg.draw.rect(surf, fg_color, (10, cy - thick // 2, icon_size[0] - 20, thick))
            else:
                pg.draw.rect(surf, fg_color, (10, cy - thick // 2, icon_size[0] - 20, thick))
            return surf
            
        plus_default = make_icon("+", (200, 200, 200), (20, 20, 20))
        plus_hover = make_icon("+", (255, 255, 255), (10, 10, 10))
        minus_default = make_icon("-", (200, 200, 200), (20, 20, 20))
        minus_hover = make_icon("-", (255, 255, 255), (10, 10, 10))
        plus_surfaces = (plus_default, plus_hover)
        minus_surfaces = (minus_default, minus_hover)
        spacing = 8
        
        # --- 💥 統一定義 Y 軸參數 💥 ---
        self.LIST_START_Y = GameSettings.SCREEN_HEIGHT // 4 + 50 
        self.LIST_OFFSET_Y = 70 # 統一使用 70 作為垂直間距
        # --------------------------------

        # --- ⚡ 商品清單定義 ---
        item_definitions = [
            {
                "name": "Attack Potion",
                "bag_name": "Attack",
                "image_path": "assets/images/ingame_ui/options5.png",
                "base_price": 10,
            },
            {
                "name": "Health Potion L", 
                "bag_name": "Heal",
                "image_path": "assets/images/ingame_ui/options6.png", 
                "base_price": 20,
            },
            {
                "name": "Mana Potion",
                "bag_name": "Mana",
                "image_path": "assets/images/ingame_ui/potion.png",
                "base_price": 15,
            },
            {
                "name": "Speed Scroll", 
                "bag_name": "Speed Scroll",
                "image_path": "assets/images/ingame_ui/ball.png", 
                "base_price": 25,
            },
        ]
        
        # --- 動態創建 ShopItem 實例 ---
        self.shop_items: list[ShopItem] = []
        for i, item_data in enumerate(item_definitions):
            # 使用統一的 LIST_START_Y 和 LIST_OFFSET_Y
            current_y = self.LIST_START_Y + i * self.LIST_OFFSET_Y
            
            item = ShopItem(
                name=item_data["name"],
                image_path=item_data["image_path"],
                base_price=item_data["base_price"],
                position_y=current_y, 
                icon_size=icon_size,
                plus_surfaces=plus_surfaces,
                minus_surfaces=minus_surfaces,
                spacing=spacing,
                game_manager=self.game_manager,
                on_change=self._on_item_changed,
                bag_name=item_data.get("bag_name")
            )
            self.shop_items.append(item)
            
        # --- 背包物品顯示 (Backpack Item Display) ---
        
        # 取得背包物品清單
        # 這裡假設 self.game_manager.bag._items_data 已經是可讀的物品列表
        backpack_item_definitions = self.game_manager.bag._items_data

        # Backpack X 座標: 將其設置在背景框架的右側區域
        self.BACKPACK_START_X = GameSettings.SCREEN_WIDTH * 3 // 4 - 100 
        
        self.backpack_items: list[BackpackItem] = []
        
        for i, item in enumerate(backpack_item_definitions):
            # 使用統一的 LIST_START_Y 和 LIST_OFFSET_Y
            current_y = self.LIST_START_Y + i * self.LIST_OFFSET_Y
            
            item_display = BackpackItem(
                name=item["name"],
                # 假設 item['sprite_path'] 不包含 'assets/images/'
                image_path=f"assets/images/{item['sprite_path']}", 
                x=self.BACKPACK_START_X,
                y=current_y,
                quantity=item["count"]
            )
            self.backpack_items.append(item_display)

    def _on_item_changed(self, name: str):
        """Called when a ShopItem changes bag contents (buy/sell).
        Sync backpack displays to current Bag state.
        """
        bag_item = self.game_manager.bag.get_item_by_name(name)

        # find existing display
        existing = None
        for b in self.backpack_items:
            if b.name == name:
                existing = b
                break

        # Keep backpack layout fixed: only update existing displays' quantities.
        # If an item was removed from Bag (bag_item is None), show 0 instead of removing the display.
        if existing:
            qty = bag_item.get("count", 0) if bag_item is not None else 0
            existing.set_quantity(qty)
        # If there's no existing display for this item, do nothing (do not add new entries)


    @override
    def enter(self) -> None:
        pass

    @override
    def exit(self) -> None:
        pass

    @override
    def update(self, dt: float) -> None:
        self.close_button.update(dt)
        # 更新所有商品項目的按鈕
        for item in self.shop_items:
            item.update(dt)

    @override
    def draw(self, screen: pg.Surface) -> None:
        # Draw dark overlay to dim game scene
        dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        dark_overlay.set_alpha(120)
        dark_overlay.fill((0, 0, 0))
        screen.blit(dark_overlay, (0, 0))
        screen.blit(self.background.image, self.background.rect)
        
        # 繪製所有商品項目的圖片、價格和按鈕
        for item in self.shop_items:
            item.draw(screen)
        
        # 繪製背包物品
        for backpack_item in self.backpack_items:
            backpack_item.draw(screen)

        # Draw close button
        self.close_button.draw(screen)