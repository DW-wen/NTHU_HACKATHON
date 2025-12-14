import pygame as pg
from src.utils import GameSettings

class Minimap:
    """A lightweight minimap that shows a scaled thumbnail of the current map
    and the player position. It uses the pre-baked map surface in Map._surface
    to produce a thumbnail for performance.
    """
    def __init__(self, game_manager, width: int = 200, height: int = 150, pos: tuple[int, int] = (8, 8)):
        self.game_manager = game_manager
        self.width = width
        self.height = height
        self.pos = pos
        self.surface = pg.Surface((width, height), pg.SRCALPHA)
        self.visible = True
        # Border colors
        self.bg_color = (0, 0, 0, 160)
        self.border_color = (255, 255, 255)
        self.player_color = (255, 0, 0)

    def update(self, dt: float):
        # Nothing heavy to update; keep method for consistency
        return

    def draw(self, screen: pg.Surface):
        if not self.visible:
            return
        if not self.game_manager or not hasattr(self.game_manager, 'current_map') or self.game_manager.current_map is None:
            return

        map_obj = self.game_manager.current_map
        map_surface = getattr(map_obj, '_surface', None)
        if map_surface is None:
            return

        # Scale the whole map surface to minimap size
        try:
            scaled = pg.transform.smoothscale(map_surface, (self.width, self.height))
        except Exception:
            scaled = pg.transform.scale(map_surface, (self.width, self.height))

        # Draw background with slight opacity
        bg = pg.Surface((self.width + 6, self.height + 6), pg.SRCALPHA)
        bg.fill(self.bg_color)
        screen.blit(bg, (self.pos[0] - 3, self.pos[1] - 3))

        # Draw the scaled map
        screen.blit(scaled, self.pos)

        # Draw player position as a circle
        player = getattr(self.game_manager, 'player', None)
        if player is not None:
            map_pixel_w = map_obj.tmxdata.width * GameSettings.TILE_SIZE
            map_pixel_h = map_obj.tmxdata.height * GameSettings.TILE_SIZE
            if map_pixel_w > 0 and map_pixel_h > 0:
                rel_x = player.position.x / map_pixel_w
                rel_y = player.position.y / map_pixel_h
                px = int(self.pos[0] + rel_x * self.width)
                py = int(self.pos[1] + rel_y * self.height)
                # clamp
                px = max(self.pos[0], min(self.pos[0] + self.width - 1, px))
                py = max(self.pos[1], min(self.pos[1] + self.height - 1, py))
                pg.draw.circle(screen, self.player_color, (px, py), 3)

        # Border
        pg.draw.rect(screen, self.border_color, (self.pos[0] - 1, self.pos[1] - 1, self.width + 2, self.height + 2), 1)

    def toggle(self):
        self.visible = not self.visible
