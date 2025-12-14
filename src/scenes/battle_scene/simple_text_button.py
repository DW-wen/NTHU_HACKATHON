import random
import pygame as pg

from src.core.managers.game_manager import GameManager

from src.core.services import scene_manager, sound_manager, input_manager
from typing import Callable, Tuple, override


class SimpleTextButton:
    """一個只使用文字和純色背景的按鈕，用於 BattleScene。"""
    
    text: str
    rect: pg.Rect
    on_click: Callable[[], None] | None
    font: pg.font.Font
    
    # 視覺屬性
    text_color: Tuple[int, int, int]
    default_color: Tuple[int, int, int]
    hover_color: Tuple[int, int, int]
    current_color: Tuple[int, int, int]

    def __init__(
        self,
        text: str,
        rect: pg.Rect,
        on_click: Callable[[], None] | None = None,
        font_size: int = 30,
        text_color: Tuple[int, int, int] = (0, 0, 0),
        default_color: Tuple[int, int, int] = (255, 255, 255, 0), # 透明/白色背景
        hover_color: Tuple[int, int, int] = (200, 200, 200)       # Hover 時的灰色背景
    ):
        self.text = text
        self.rect = rect
        self.on_click = on_click
        self.text_color = text_color
        self.default_color = default_color
        self.hover_color = hover_color
        self.current_color = default_color
        
        # 字體初始化
        try:
            self.font = pg.font.SysFont("SimHei", font_size)
        except pg.error:
            self.font = pg.font.Font(None, font_size)
            
        self._render_text()

    def _render_text(self):
        """渲染文字表面並計算其位置 (置中)"""
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def update(self, dt: float) -> None:
        mouse_pos = input_manager.mouse_pos # 假設 input_manager 可用

        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color # 變更為 Hover 顏色
            
            # 檢查滑鼠左鍵點擊
            if input_manager.mouse_pressed(1) and self.on_click is not None:
                self.on_click()
        else:
            self.current_color = self.default_color # 恢復預設顏色

    def draw(self, screen: pg.Surface) -> None:
        # 如果背景顏色不是透明 (alpha=0)，則繪製背景矩形
        if len(self.current_color) == 4 and self.current_color[3] > 0 or len(self.current_color) == 3:
            pg.draw.rect(screen, self.current_color, self.rect)
            
        # 繪製文字
        screen.blit(self.text_surface, self.text_rect)