from src.interface.components import Button
from src.utils import Logger, GameSettings
import pygame as pg
from typing import Optional, Callable

class ShopItem:
    """代表商店中的一個可購買/出售的商品及其相關UI元素。"""
    def __init__(
        self,
        name: str,
        image_path: str,
        base_price: int,
        position_y: int,
        icon_size: tuple[int, int],
        plus_surfaces: tuple[pg.Surface, pg.Surface],
        minus_surfaces: tuple[pg.Surface, pg.Surface],
        spacing: int,
        game_manager=None,
        on_change: Optional[Callable[[str], None]] = None,
        bag_name: str | None = None,
    ):
        self.name = name
        self.base_price = base_price
        self.current_price = base_price  # 可以是浮動價格
        self.image_path = image_path
        self.icon_size = icon_size
        self.spacing = spacing

        # --- 圖像和表面 ---
        self.image = pg.image.load(image_path)
        self.image = pg.transform.scale(self.image, icon_size)

        # 價格顯示
        self._price_font = pg.font.SysFont("inkfree", 30)
        # 這裡應該使用當前的價格 self.current_price
        self.price_surface = self._price_font.render(f"P: {self.current_price}", True, (255, 255, 255))
        
        # 獲取價格寬度 (price_w) 和圖標尺寸 (icon_w)
        icon_w, icon_h = self.icon_size
        price_w = self.price_surface.get_width()
        
        # --- 修正位置計算：使 (Price | - | Item | +) 區塊水平置中 ---
        
        # 1. 計算整個 ShopItem 區塊的總寬度 (W_Total)
        # W_Total = Price_W + Spacing + Minus_W + Spacing + Item_W + Spacing + Plus_W
        # 假設 Minus 和 Plus 按鈕與 Item Icon 尺寸相同
        W_Total = price_w + self.spacing * 3 + icon_w * 3 
        
        # 2. 確定起點 X (最左側元素 Price 的 X 座標)
        # X_Start: 讓整個區塊 W_Total 在螢幕中居中
        X_Start = (GameSettings.SCREEN_WIDTH // 5 + 70) - (W_Total // 2)
        
        # 3. 確定中心 Y 軸
        self.y_pos = position_y 
        
        current_x = X_Start
        
        # A. 商品圖片 (Item / Potion)
        self.potion_pos = (current_x, self.y_pos) # Item 圖標的左上角
        current_x += icon_w + self.spacing
        
        # B. 加號按鈕 (Plus Button)
        plus_x = current_x
        current_x += icon_w + self.spacing
        
        # C. 減號按鈕 (Minus Button)
        minus_x = current_x
        current_x += icon_w + self.spacing
        
        # D. 價格 (Price)
        # Price 的 X 位置 (左上角)
        self.price_pos = (
            current_x, 
            self.y_pos + (icon_h - self.price_surface.get_height()) // 2 # 垂直居中
        )
        
        # --- 按鈕實例化 (使用修正後的座標) ---
        
        # 減號按鈕 (-) (出售)
        self.minus_button = Button(
            minus_surfaces[0], minus_surfaces[1],
            minus_x, self.y_pos, icon_w, icon_h,
            lambda: self.sell_item()
        )

        # 加號按鈕 (+) (購買)
        self.plus_button = Button(
            plus_surfaces[0], plus_surfaces[1],
            plus_x, self.y_pos, icon_w, icon_h,
            lambda: self.buy_item()
        )
        # GameManager reference for interacting with Bag / coins
        self.game_manager = game_manager
        # Callback to notify the scene to refresh backpack UI
        self.on_change = on_change
        # The name used inside Bag for this item (may differ from displayed name)
        self.bag_name = bag_name if bag_name is not None else self.name

    # --- 購買/出售邏輯 ---
    def buy_item(self):
        """處理購買邏輯。"""
        Logger.info(f"Buy {self.name} for {self.current_price}")
        if self.game_manager is None:
            Logger.warning("No GameManager available for buy action")
            return

        bag = self.game_manager.bag
        coin_item = bag.get_item_by_name("Coins")
        current_coins = coin_item.get("count", 0) if coin_item else 0
        if current_coins < self.current_price:
            Logger.info("Not enough coins to buy")
            return

        # Deduct coins
        bag.change_item_count("Coins", -self.current_price)

        # Add the purchased item (sprite path from ShopItem.image_path)
        sprite_path = ""
        if isinstance(self.image_path, str) and self.image_path.startswith("assets/images/"):
            sprite_path = self.image_path.replace("assets/images/", "")
        else:
            sprite_path = self.image_path

        bag.change_item_count(self.bag_name, +1, sprite_path)
        # Notify scene to refresh backpack UI (use bag_name)
        if self.on_change:
            self.on_change(self.bag_name)
            # also refresh coins display
            self.on_change("Coins")

    def sell_item(self):
        """處理出售邏輯。"""
        Logger.info(f"Sell {self.name} for {self.current_price}")
        if self.game_manager is None:
            Logger.warning("No GameManager available for sell action")
            return

        bag = self.game_manager.bag
        item = bag.get_item_by_name(self.bag_name)
        if item is None or item.get("count", 0) <= 0:
            Logger.info("No item to sell")
            return

        # Decrease item count
        bag.change_item_count(self.bag_name, -1)
        # Increase coins by price
        bag.change_item_count("Coins", +self.current_price)

        if self.on_change:
            self.on_change(self.bag_name)
            # also refresh coins display
            self.on_change("Coins")
    def update_price_display(self):
        """更新價格顯示的 Surface。"""
        # 價格可能在遊戲中途變動，呼叫此方法可更新顯示
        self.price_surface = self._price_font.render(f"P: {self.current_price}", True, (255, 255, 255))


    # --- 介面方法 ---
    def update(self, dt: float):
        """更新按鈕狀態。"""
        self.minus_button.update(dt)
        self.plus_button.update(dt)

    def draw(self, screen: pg.Surface):
        """繪製商品圖片、價格和按鈕。"""
        # 繪製商品圖片 (Potion)
        screen.blit(self.image, self.potion_pos)
        
        # 繪製價格
        screen.blit(self.price_surface, self.price_pos)

        # 繪製按鈕
        self.minus_button.draw(screen)
        self.plus_button.draw(screen)