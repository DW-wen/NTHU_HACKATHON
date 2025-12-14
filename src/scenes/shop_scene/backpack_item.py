import pygame as pg

from src.core.managers.game_manager import GameManager


class BackpackItem:
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