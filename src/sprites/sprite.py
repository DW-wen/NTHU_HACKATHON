import pygame as pg
from src.core.services import resource_manager
from src.utils import Position, PositionCamera
from typing import Optional
from pygame.surface import Surface

class Sprite:
    image: pg.Surface
    rect: pg.Rect
    
    def __init__(self, img_path: str | pg.Surface, size: tuple[int, int] | None = None):
        # 判斷傳入的是路徑字串還是 Surface 物件
        if isinstance(img_path, str):
            # 傳入的是路徑字串，使用資源管理器載入
            self.image = resource_manager.get_image(img_path)
        elif isinstance(img_path, Surface):
            # 傳入的是 Surface 物件 (例如：已翻轉的圖像)，直接使用
            self.image = img_path
        else:
            raise TypeError("Sprite 構造函數必須接受檔案路徑字串或 pygame.Surface 物件。")
            
        # 縮放邏輯保持不變
        if size is not None:
            self.image = pg.transform.scale(self.image, size)
            
      
        self.rect = self.image.get_rect()
        
    def update(self, dt: float):
        pass

    def draw(self, screen: pg.Surface, camera: Optional[PositionCamera] = None):
        if camera is not None:
            screen.blit(self.image, camera.transform_rect(self.rect))
        else:
            screen.blit(self.image, self.rect)
        
    def draw_hitbox(self, screen: pg.Surface, camera: Optional[PositionCamera] = None):
        if camera is not None:
            pg.draw.rect(screen, (255, 0, 0), camera.transform_rect(self.rect), 1)
        else:
            pg.draw.rect(screen, (255, 0, 0), self.rect, 1)
        
    def update_pos(self, pos: Position):
        self.rect.topleft = (round(pos.x), round(pos.y))