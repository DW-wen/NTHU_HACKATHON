import random
import pygame as pg

from saves.load_data import load_save
from src.core.managers.game_manager import GameManager
from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from typing import Callable, Tuple, override

PLAYER_TURN = "PLAYER_TURN"
ENEMY_TURN = "ENEMY_TURN"
WAIT_FOR_INPUT = "WAIT_FOR_INPUT"
ACTION_ANIMATION = "ACTION_ANIMATION"
GAME_OVER = "GAME_OVER"

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

class BattleScene(Scene):
    # Background Image
    background: BackgroundSprite
    # Buttons
    attack_button: SimpleTextButton 
    run_button: SimpleTextButton    
    
    # Battle menu background
    menu_bg: pg.Surface
    menu_bg_rect: pg.Rect
    
    # --- Battle System Properties ---
    battle_state: str
    message_text: str
    message_font: pg.font.Font
    # -----------------------------
    
    # Message box properties
    message_box: pg.Surface
    message_box_rect: pg.Rect
    
    myPokemon: 'PokemonDisplay'
    enemyPokemon: 'PokemonDisplay'

    def __init__(self, game_manager: GameManager):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.game_manager = game_manager
        
        self.myPokemon = None # type: ignore
        self.enemyPokemon = None # type: ignore
        # Initialize battle state and message
        self.battle_state = WAIT_FOR_INPUT # Battle starts waiting for input
        try:
            self.message_font = pg.font.SysFont("Arial", 24)
        except pg.error:
            self.message_font = pg.font.Font(None, 24)
            
        self.message_text = "Battle started! It's your turn. Select an action."
        
        # Player Pokémon
        my_mon = self.game_manager.bag._monsters_data[0]
        self.myPokemon = PokemonDisplay(
                    sprite_path=f"assets/images/{my_mon['sprite_path']}",
                    # Adjust position for a traditional layout (bottom-left)
                    x=GameSettings.SCREEN_WIDTH // 10 - 30,
                    y=GameSettings.SCREEN_HEIGHT * 3 // 4 - 20,
                    hp_current=my_mon["hp"],
                    hp_max=my_mon["max_hp"],
                    level=my_mon["level"]
                )
        
        # Enemy Pokémon (assuming index 2 exists)
        enemy_mon = self.game_manager.bag._monsters_data[2]
        self.enemyPokemon = PokemonDisplay(
                    sprite_path=f"assets/images/{enemy_mon['sprite_path']}",
                    # Adjust position for a traditional layout (top-right)
                    x=GameSettings.SCREEN_WIDTH * 6 // 10 - 30,
                    y=GameSettings.SCREEN_HEIGHT // 10 - 20,
                    hp_current=enemy_mon["hp"],
                    hp_max=enemy_mon["max_hp"],
                    level=enemy_mon["level"]
                )
        
        # --- Battle Menu and Button Setup ---
        menu_height = 100 
        UI_BAR_PATH = "assets/images/UI/raw/UI_Flat_Bar01a.png"
        
        try:
            self.menu_bg = pg.image.load(UI_BAR_PATH).convert_alpha()
            self.menu_bg = pg.transform.scale(self.menu_bg, (GameSettings.SCREEN_WIDTH, menu_height))
        except pg.error:
            self.menu_bg = pg.Surface((GameSettings.SCREEN_WIDTH, menu_height))
            self.menu_bg.fill((255, 255, 255))
            
        self.menu_bg_rect = self.menu_bg.get_rect(
            bottomleft=(0, GameSettings.SCREEN_HEIGHT)
        ) 
        
        # Initialize overlay message box (semi-transparent black)
        box_width = GameSettings.SCREEN_WIDTH
        box_height = 100
        self.message_box = pg.Surface((box_width, box_height), pg.SRCALPHA)
        self.message_box.fill((0, 0, 0, 180)) # Black, opacity 180/255
        self.message_box_rect = self.message_box.get_rect(
            bottomleft=(0, GameSettings.SCREEN_HEIGHT)
        )
        
        # Calculate button positions
        button_width = 150
        button_height = 50
        padding = 50
        
        # 1. Attack Button
        attack_rect = pg.Rect(
            self.menu_bg_rect.left + padding, 
            self.menu_bg_rect.centery - button_height // 2, 
            button_width, 
            button_height
        )
        self.attack_button = SimpleTextButton(
            text="Attack",  
            rect=attack_rect,
            on_click=self.handle_attack,
            font_size=28,
            text_color=(0, 0, 0), 
            default_color=(255, 255, 255, 0), 
            hover_color=(220, 220, 220, 150)
        )
        
        # 2. Run Button
        run_rect = pg.Rect(
            self.menu_bg_rect.right - button_width - padding, 
            self.menu_bg_rect.centery - button_height // 2, 
            button_width, 
            button_height
        )
        self.run_button = SimpleTextButton(
            text="Run", 
            rect=run_rect,
            on_click=self.handle_run,
            font_size=28,
            text_color=(0, 0, 0),
            default_color=(255, 255, 255, 0), 
            hover_color=(220, 220, 220, 150)
        )
        
    # --- Battle System Core Methods ---
    def pre_battle_check(self) -> bool:
        """
        檢查玩家或敵方 Pokémon 在進入戰鬥時是否已經 fainted。
        如果有人 fainted，則直接結束戰鬥並返回 True。
        """
        if self.myPokemon.hp_current <= 0:
            # 玩家 Pokémon fainted
            self.message_text = "Your Pokémon fainted before battle started! Returning to map."
            self.battle_state = GAME_OVER
            scene_manager.change_scene("game")
            return True
            
        elif self.enemyPokemon.hp_current <= 0:
            # 敵方 Pokémon fainted (理論上不應該發生，但作為防禦性編程)
            self.message_text = "Enemy Pokémon already fainted! Returning to map."
            self.battle_state = GAME_OVER
            scene_manager.change_scene("game")
            return True
            
        return False
    
    def check_for_game_over(self, next_state: str) -> bool:
        # 修正: 將 monsters[0] 改為 _monsters_data[0]
        self.game_manager.bag._monsters_data[0]["hp"] = self.myPokemon.hp_current 
        
        """Checks if the player or enemy is defeated (HP <= 0), sets message, and returns True if game over."""
        if self.myPokemon.hp_current <= 0:
            # ... (略)
            return True
        elif self.enemyPokemon.hp_current <= 0:
            self.battle_state = GAME_OVER
            # 修正: 將 monsters[2] 改為 _monsters_data[2]
            self.game_manager.bag._monsters_data[2]["hp"] = self.enemyPokemon.hp_current
            self.message_text = f"Enemy Pokémon fainted! You won! (Press SPACE to return)"
            return True
        return False

    def handle_attack(self):
        """Handles player's Attack action"""
        if self.battle_state != WAIT_FOR_INPUT:
            return
            
        # Attack calculation (simplified to fixed damage)
        damage = 20
        new_hp = max(0, self.enemyPokemon.hp_current - damage)
        self.enemyPokemon.set_hp(new_hp)
        
        # Set message and enter message delay state
        self.message_text = f"Your Pokémon attacked! (Press SPACE to continue)"
        self.battle_state = ACTION_ANIMATION

    def handle_run(self):
        """Handles Run button click - enters message delay state for confirmation"""
        if self.battle_state != WAIT_FOR_INPUT:
            return
        # 修正: 將 monsters[0] 改為 _monsters_data[0]
        self.game_manager.bag._monsters_data[0]["hp"] = self.myPokemon.hp_current
        self.message_text = "Successfully escaped! (Press SPACE to return to map)"
        self.battle_state = ACTION_ANIMATION

    def handle_enemy_turn_logic(self):
        """Executes the enemy's action logic (damage calculation)"""
        if self.check_for_game_over(GAME_OVER):
            return

        # Enemy action logic (simplified to only attack)
        
        # Attack calculation (simplified to random damage)
        damage = random.randint(15, 25)
        new_hp = max(0, self.myPokemon.hp_current - damage)
        self.myPokemon.set_hp(new_hp)
        
        # Set message and enter message delay state
        self.message_text = f"Enemy Pokémon attacked! (Press SPACE to continue)"
        self.battle_state = ACTION_ANIMATION

    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg")
        # 玩家 Pokémon
        my_mon = self.game_manager.bag._monsters_data[0] 
        self.myPokemon = PokemonDisplay(
                            sprite_path=f"assets/images/{my_mon['sprite_path']}",
                            x=GameSettings.SCREEN_WIDTH // 10 - 30,
                            y=GameSettings.SCREEN_HEIGHT * 3 // 4 - 20,
                            hp_current=my_mon["hp"],
                            hp_max=my_mon["max_hp"],
                            level=my_mon["level"]
                        )
        
        # 敵方 Pokémon
        enemy_mon = self.game_manager.bag._monsters_data[2]
        self.enemyPokemon = PokemonDisplay(
                            sprite_path=f"assets/images/{enemy_mon['sprite_path']}",
                            x=GameSettings.SCREEN_WIDTH * 6 // 10 - 30,
                            y=GameSettings.SCREEN_HEIGHT // 10 - 20,
                            hp_current=enemy_mon["hp"],
                            hp_max=enemy_mon["max_hp"],
                            level=enemy_mon["level"]
                        )
        
        # 執行戰鬥前的檢查
        if self.pre_battle_check():
            return
            
        self.battle_state = WAIT_FOR_INPUT
        self.message_text = "Battle started! It's your turn. Select an action."
        
        # 確保更新後的 HP/狀態已寫回 GameManager (雖然這邏輯應該在 check_for_game_over 中，但作為防禦性編程)
        self.game_manager.bag._monsters_data[0]["hp"] = self.myPokemon.hp_current
        self.game_manager.bag._monsters_data[2]["hp"] = self.enemyPokemon.hp_current

    @override
    def exit(self) -> None:
        pass

    @override
    def update(self, dt: float) -> None:
        
        if self.battle_state == WAIT_FOR_INPUT:
            self.attack_button.update(dt)
            self.run_button.update(dt)
            
        elif self.battle_state == ENEMY_TURN:
            # Execute enemy action logic and switch to ACTION_ANIMATION state
            self.handle_enemy_turn_logic()
            
        elif self.battle_state == ACTION_ANIMATION:
            # Message delay state: wait for player to press SPACE
            if input_manager.key_pressed(pg.K_SPACE):
                
                # 1. Check if it's the Run message
                if "return to map" in self.message_text:
                    scene_manager.change_scene("game")
                    return

                # 2. Check if the game is already over
                if self.check_for_game_over(GAME_OVER):
                    return
                    
                # 3. Determine the next turn
                # If player just attacked, the next step is the enemy turn
                if "Your Pokémon attacked" in self.message_text:
                    self.battle_state = ENEMY_TURN 
                # If enemy just attacked, the next step is player input
                elif "Enemy Pokémon attacked" in self.message_text:
                    self.battle_state = WAIT_FOR_INPUT
                    self.message_text = "It's your turn. Select an action."
            
        elif self.battle_state == GAME_OVER:
            # Game Over state: wait for SPACE to switch scene
            if input_manager.key_pressed(pg.K_SPACE):
                scene_manager.change_scene("game")

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        self.myPokemon.draw(screen)
        self.enemyPokemon.draw(screen) 
        
        # Draw battle menu background
        screen.blit(self.menu_bg, self.menu_bg_rect)
        
        # Only draw buttons when waiting for input (on top of the menu background)
        if self.battle_state == WAIT_FOR_INPUT:
            self.attack_button.draw(screen)
            self.run_button.draw(screen)
        
        # Draw the **overlay** message box and text (for ACTION_ANIMATION, GAME_OVER)
        if self.battle_state == ACTION_ANIMATION or self.battle_state == GAME_OVER:
            # Draw semi-transparent black overlay
            screen.blit(self.message_box, self.message_box_rect)
            
            # Draw battle message (text color changed to white for visibility on black background)
            msg_surface = self.message_font.render(self.message_text, True, (255, 255, 255))
            
            # Center the message on the message_box
            msg_rect = msg_surface.get_rect(center=self.message_box_rect.center)
            screen.blit(msg_surface, msg_rect)
        
        # If in WAIT_FOR_INPUT state, draw the message in the clear area of the menu
        elif self.battle_state == WAIT_FOR_INPUT:
             # Draw battle message (centered above the menu background)
            msg_surface = self.message_font.render(self.message_text, True, (0, 0, 0))
            msg_rect = msg_surface.get_rect(midtop=(self.menu_bg_rect.centerx, self.menu_bg_rect.top + 5))
            screen.blit(msg_surface, msg_rect)



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

    def draw(self, screen: pg.Surface):
        """畫出完整 Pokémon 區塊"""
        screen.blit(self.bg, self.bg_rect)
        screen.blit(self.sprite, self.sprite_rect)
        screen.blit(self.hp_surface, self.hp_rect)
        screen.blit(self.level_surface, self.level_rect)
       