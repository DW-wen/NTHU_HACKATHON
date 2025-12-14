import pygame as pg

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
        from src.utils.definition import clamp_level
        self.level = clamp_level(level)


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
        from src.utils.definition import clamp_level
        self.level = clamp_level(level)
        self.update_text()

    def draw(self, screen: pg.Surface):
        """畫出完整 Pokémon 區塊"""
        screen.blit(self.bg, self.bg_rect)
        screen.blit(self.sprite, self.sprite_rect)
        screen.blit(self.hp_surface, self.hp_rect)
        screen.blit(self.level_surface, self.level_rect)