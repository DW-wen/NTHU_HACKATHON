import pygame as pg
from typing import Optional


class ChatOverlay:
    """Simple chat overlay: shows recent messages and allows typing.

    Controls:
    - Press Enter to open/submit chat input.
    - Type to enter text, Backspace to delete.
    """

    def __init__(self, online_manager, width: int = 500, height: int = 160, pos: tuple[int, int] = (8, 520)):
        self.online_manager = online_manager
        self.width = width
        self.height = height
        self.pos = pos
        self.font = pg.font.SysFont('Arial', 18)
        self.active = False
        self.input_text = ""
        self.max_lines = 6
        self._messages: list[dict] = []

    def handle_event(self, event: pg.event.EventType) -> None:
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                if self.active:
                    # submit
                    text = self.input_text.strip()
                    if text and self.online_manager:
                        self.online_manager.send_chat(text)
                    self.input_text = ""
                    self.active = False
                else:
                    # open input
                    self.active = True
            elif self.active:
                if event.key == pg.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    char = getattr(event, 'unicode', '')
                    if char:
                        self.input_text += char

    def update(self, dt: float) -> None:
        # pull recent messages from online manager
        if self.online_manager:
            msgs = self.online_manager.get_recent_chat(self.max_lines)
            # messages are dicts with id, from, text, ts
            self._messages = msgs[-self.max_lines:]

    def draw(self, screen: pg.Surface) -> None:
        x, y = self.pos
        # Background
        s = pg.Surface((self.width, self.height), pg.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (x, y))

        # Draw messages
        pad = 8
        line_h = 22
        start_y = y + pad
        for i, m in enumerate(self._messages):
            text = f"P{m.get('from', '?')}: {m.get('text', '')}"
            surf = self.font.render(text, True, (255, 255, 255))
            screen.blit(surf, (x + pad, start_y + i * line_h))

        # Input box
        box_y = y + self.height - 30
        box_rect = pg.Rect(x + pad, box_y, self.width - pad * 2, 22)
        pg.draw.rect(screen, (255, 255, 255), box_rect, 1)
        if self.active:
            display = self.input_text + "|"
        else:
            display = "Press Enter to chat"
        surf = self.font.render(display, True, (255, 255, 255))
        screen.blit(surf, (box_rect.x + 4, box_rect.y + 2))
