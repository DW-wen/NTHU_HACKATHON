import pygame as pg
import random
from typing import override, Dict, Any, Optional

# 核心依賴
from src.core.managers.game_manager import GameManager
from src.scenes.battle_scene.pokemon_display import PokemonDisplay
from src.scenes.battle_scene.simple_text_button import SimpleTextButton
from src.utils import GameSettings
from src.utils import Logger
from src.sprites import BackgroundSprite
from src.scenes.scene import Scene
from src.core.services import scene_manager, sound_manager, input_manager

# 匯入分離的邏輯和數據
from src.scenes.battle_scene.element_data import get_element_from_sprite_path
from src.scenes.battle_scene.battle_logic import BattleLogic # 核心變動

# 確保 BattleScene 能夠訪問這些類型 (如果需要)
try:
    from src.utils.definition import clamp_level
except ImportError:
    def clamp_level(level: int) -> int:
        lv = int(level) if isinstance(lv, int) else 1
        return max(1, lv)

# 狀態常量
PLAYER_TURN = "PLAYER_TURN"
ENEMY_TURN = "ENEMY_TURN"
WAIT_FOR_INPUT = "WAIT_FOR_INPUT"
ACTION_ANIMATION = "ACTION_ANIMATION"
GAME_OVER = "GAME_OVER"


class BattleScene(Scene):
    # ... (屬性定義保持不變)
    background: BackgroundSprite
    attack_button: SimpleTextButton 
    run_button: SimpleTextButton     
    menu_bg: pg.Surface
    menu_bg_rect: pg.Rect
    battle_state: str
    message_text: str
    message_font: pg.font.Font
    message_box: pg.Surface
    message_box_rect: pg.Rect
    myPokemon: 'PokemonDisplay'
    enemyPokemon: 'PokemonDisplay'
    
    # 核心新增：分離的戰鬥邏輯實例
    battle_logic: 'BattleLogic' 

    def __init__(self, game_manager: GameManager):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.game_manager = game_manager
        
        # 實例化戰鬥邏輯
        self.battle_logic = BattleLogic(game_manager)

        self.myPokemon = None # type: ignore
        self.enemyPokemon = None # type: ignore
        self.battle_state = WAIT_FOR_INPUT 
        
        try:
            self.message_font = pg.font.SysFont("Arial", 24)
        except pg.error:
            self.message_font = pg.font.Font(None, 24)
            
        self.message_text = "Battle started! It's your turn. Select an action."
        
        # --- 數據初始化 (確保元素屬性存在於數據中) ---
        try:
            my_mon = self.game_manager.bag._monsters_data[0]
            enemy_mon = self.game_manager.bag._monsters_data[2]
            
            # 確保數據中存有 element 屬性
            my_mon["element"] = get_element_from_sprite_path(my_mon['sprite_path'])
            enemy_mon["element"] = get_element_from_sprite_path(enemy_mon['sprite_path'])

            # Player Pokémon Display
            self.myPokemon = PokemonDisplay(
                sprite_path=f"assets/images/{my_mon['sprite_path']}",
                x=GameSettings.SCREEN_WIDTH // 10 - 30,
                y=GameSettings.SCREEN_HEIGHT * 3 // 4 - 20,
                hp_current=my_mon["hp"],
                hp_max=my_mon["max_hp"],
                level=my_mon["level"]
            )
            
            # Enemy Pokémon Display
            self.enemyPokemon = PokemonDisplay(
                sprite_path=f"assets/images/{enemy_mon['sprite_path']}",
                x=GameSettings.SCREEN_WIDTH * 6 // 10 - 30,
                y=GameSettings.SCREEN_HEIGHT // 10 - 20,
                hp_current=enemy_mon["hp"],
                hp_max=enemy_mon["max_hp"],
                level=enemy_mon["level"]
            )
        except IndexError:
            Logger.error("BattleScene __init__: Missing player or enemy Pokémon data. Using fallback setup.")
            # ... (如果需要，在這裡加入錯誤處理或默認的 Pokemon 設置) ...

        # ... (Button 和 UI 初始化邏輯保持不變) ...
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
        
        box_width = GameSettings.SCREEN_WIDTH
        box_height = 100
        self.message_box = pg.Surface((box_width, box_height), pg.SRCALPHA)
        self.message_box.fill((0, 0, 0, 180)) 
        self.message_box_rect = self.message_box.get_rect(
            bottomleft=(0, GameSettings.SCREEN_HEIGHT)
        )
        
        button_width = 150
        button_height = 50
        padding = 50
        
        attack_rect = pg.Rect(self.menu_bg_rect.left + padding, self.menu_bg_rect.centery - button_height // 2, button_width, button_height)
        self.attack_button = SimpleTextButton(text="Attack", rect=attack_rect, on_click=self.handle_attack, font_size=28, text_color=(0, 0, 0), default_color=(255, 255, 255, 0), hover_color=(220, 220, 220, 150))
        
        run_rect = pg.Rect(self.menu_bg_rect.right - button_width - padding, self.menu_bg_rect.centery - button_height // 2, button_width, button_height)
        self.run_button = SimpleTextButton(text="Run", rect=run_rect, on_click=self.handle_run, font_size=28, text_color=(0, 0, 0), default_color=(255, 255, 255, 0), hover_color=(220, 220, 220, 150))
        
        item_w = 110
        item_h = 40
        center_x = (attack_rect.right + run_rect.left) // 2
        items_x_start = center_x - (item_w * 4 + 20) // 2
        heal_rect = pg.Rect(items_x_start, self.menu_bg_rect.centery - item_h // 2, item_w, item_h)
        str_rect = pg.Rect(items_x_start + item_w + 10, heal_rect.y, item_w, item_h)
        def_rect = pg.Rect(items_x_start + (item_w + 10) * 2, heal_rect.y, item_w, item_h)
        evo_rect = pg.Rect(items_x_start + (item_w + 10) * 3, heal_rect.y, item_w, item_h)

        self.heal_button = SimpleTextButton(text="Heal", rect=heal_rect, on_click=lambda: self.handle_use_item("Heal"), font_size=28, text_color=(0, 0, 0), default_color=(255, 255, 255, 0), hover_color=(220, 220, 220, 150))
        self.str_button = SimpleTextButton(text="Strength", rect=str_rect, on_click=lambda: self.handle_use_item("Attack"), font_size=28, text_color=(0, 0, 0), default_color=(255, 255, 255, 0), hover_color=(220, 220, 220, 150))
        self.def_button = SimpleTextButton(text="Defense", rect=def_rect, on_click=lambda: self.handle_use_item("Defense"), font_size=28, text_color=(0, 0, 0), default_color=(255, 255, 255, 0), hover_color=(220, 220, 220, 150))
        self.evolve_button = SimpleTextButton(text="Evolve", rect=evo_rect, on_click=self.handle_evolve, font_size=28, text_color=(0, 0, 0), default_color=(255, 255, 255, 0), hover_color=(220, 220, 220, 150))
        
        self._next_state_after_animation: str | None = None
        
    # --- Battle System Core Methods ---

    # (pre_battle_check 和 check_for_game_over 保持不變，因為它們是 Scene 狀態轉換的關鍵)

    def pre_battle_check(self) -> bool:
        """檢查 Pokémon 是否 fainted，並在必要時結束戰鬥。"""
        if self.myPokemon is None or self.enemyPokemon is None:
            Logger.error("Pokémon Display objects are missing!")
            self.message_text = "Battle setup error! Returning to map."
            self.battle_state = GAME_OVER
            return True

        if self.myPokemon.hp_current <= 0:
            self.message_text = "Your Pokémon fainted before battle started! Returning to map."
            self.battle_state = GAME_OVER
            return True
        elif self.enemyPokemon.hp_current <= 0:
            self.message_text = "Enemy Pokémon already fainted! Returning to map."
            self.battle_state = GAME_OVER
            return True
        return False
    
    def check_for_game_over(self, next_state: str) -> bool:
        # 更新 HP 到 GameManager
        self.game_manager.bag._monsters_data[0]["hp"] = self.myPokemon.hp_current 
        
        if self.myPokemon.hp_current <= 0:
            self.battle_state = GAME_OVER
            self.message_text = f"Your Pokémon fainted! You lost! (Press SPACE to return)"
            return True
        elif self.enemyPokemon.hp_current <= 0:
            # --- 玩家獲勝，執行升級邏輯 ---
            
            player_mon = self.game_manager.bag._monsters_data[0]
            current_level = player_mon.get("level", 1)
            
            # 1. 檢查並執行升級
            # 注意：這裡使用 BattleScene 頂部定義的 clamp_level(min 1, max 3)
            # 如果您想移除 Level 3 的上限，請修改 clamp_level 的定義。
            new_level = current_level + 1
            
            # 使用 clamp_level 確保等級在限制範圍內 (雖然這裡+1應該不會超過3太多)
            clamped_new_level = clamp_level(new_level) 
            
            # 2. 應用屬性提升 (假設每升一級 Max HP + 50)
            hp_gain = 50
            player_mon["level"] = clamped_new_level
            player_mon["max_hp"] += hp_gain
            player_mon["hp"] = player_mon["max_hp"] # 補滿 HP
            
            # 3. 更新顯示物件
            if self.myPokemon:
                self.myPokemon.set_level(player_mon["level"])
                self.myPokemon.hp_max = player_mon["max_hp"]
                self.myPokemon.set_hp(player_mon["hp"])

            # 4. 設置勝利訊息
            self.battle_state = GAME_OVER
            self.game_manager.bag._monsters_data[2]["hp"] = self.enemyPokemon.hp_current
            self.message_text = f"Enemy Pokémon fainted! You won! Your Pokémon leveled up to Level {clamped_new_level}! (Press SPACE to return)"
            return True
        return False

    def handle_attack(self):
        """處理玩家的攻擊動作 (調用 BattleLogic)"""
        if self.battle_state != WAIT_FOR_INPUT: return
        if self.enemyPokemon is None: return

        # 使用 BattleLogic 計算傷害
        damage, bonus, attacker_elem = self.battle_logic.calculate_player_attack_damage()

        new_hp = max(0, self.enemyPokemon.hp_current - damage)
        self.enemyPokemon.set_hp(new_hp)
        
        # 根據 bonus 設置訊息
        if bonus > 0:
            self.message_text = f"Your {attacker_elem} Pokémon attacked for {damage} damage! It was super effective! (Press SPACE to continue)"
        elif bonus < 0:
            self.message_text = f"Your {attacker_elem} Pokémon attacked for {damage} damage. It wasn't very effective. (Press SPACE to continue)"
        else:
            self.message_text = f"Your Pokémon attacked for {damage} damage! (Press SPACE to continue)"
            
        self.battle_state = ACTION_ANIMATION 
        self._next_state_after_animation = ENEMY_TURN

    def handle_run(self):
        """處理逃跑動作"""
        if self.battle_state != WAIT_FOR_INPUT: return
        self.game_manager.bag._monsters_data[0]["hp"] = self.myPokemon.hp_current
        self.message_text = "Successfully escaped! (Press SPACE to return to map)"
        self.battle_state = ACTION_ANIMATION
        self._next_state_after_animation = "RETURN_TO_MAP"

    def handle_enemy_turn_logic(self):
        """處理敵人的攻擊動作 (調用 BattleLogic)"""
        if self.check_for_game_over(GAME_OVER): return
        if self.myPokemon is None: return

        # 使用 BattleLogic 計算傷害
        damage, bonus, attacker_elem = self.battle_logic.calculate_enemy_attack_damage()
        
        new_hp = max(0, self.myPokemon.hp_current - damage)
        self.myPokemon.set_hp(new_hp)
        
        # 根據 bonus 設置訊息
        if bonus > 0:
            self.message_text = f"Enemy {attacker_elem} Pokémon attacked for {damage} damage! It was super effective! (Press SPACE to continue)"
        elif bonus < 0:
            self.message_text = f"Enemy {attacker_elem} Pokémon attacked for {damage} damage. It wasn't very effective. (Press SPACE to continue)"
        else:
            self.message_text = f"Enemy Pokémon attacked for {damage} damage! (Press SPACE to continue)"
            
        self.battle_state = ACTION_ANIMATION 
        self._next_state_after_animation = WAIT_FOR_INPUT

    def handle_use_item(self, item_name: str):
        """處理物品使用動作 (調用 BattleLogic)"""
        if self.battle_state != WAIT_FOR_INPUT: return

        # 使用 BattleLogic 處理物品效果和庫存
        msg, success = self.battle_logic.apply_item_effect(item_name)
        
        # 如果物品使用成功，更新顯示
        if success:
            player_mon = self.game_manager.bag._monsters_data[0]
            # 必須手動同步 HP 的更新，因為 BattleLogic 直接修改了 game_manager.bag._monsters_data[0]["hp"]
            self.myPokemon.set_hp(player_mon.get("hp", self.myPokemon.hp_current))
            
            # 判斷下一步狀態：只有攻擊物品後才輪到敵人
            if item_name in ["Attack", "Defense", "Heal"]:
                 self._next_state_after_animation = ENEMY_TURN
            else:
                 self._next_state_after_animation = WAIT_FOR_INPUT
        else:
            # 如果失敗（例如庫存不足），下一輪仍然是玩家
            self._next_state_after_animation = WAIT_FOR_INPUT


        self.message_text = f"{msg} (Press SPACE to continue)"
        self.battle_state = ACTION_ANIMATION

    def handle_evolve(self):
        """處理進化動作 (調用 BattleLogic)"""
        if self.battle_state != WAIT_FOR_INPUT: return
            
        # 使用 BattleLogic 處理進化
        msg, success = self.battle_logic.try_evolve_pokemon()

        # 如果進化成功，更新顯示
        if success:
            p = self.game_manager.bag._monsters_data[0]
            # 更新 Sprite/Display
            self.myPokemon.sprite = pg.transform.scale(pg.image.load(f"assets/images/{p['sprite_path']}"), (70, 70))
            self.myPokemon.set_level(p["level"])
            self.myPokemon.hp_max = p["max_hp"] # 更新最大 HP
            self.myPokemon.set_hp(p["hp"]) # 更新當前 HP (已回滿)
            
            self._next_state_after_animation = ENEMY_TURN
        else:
            self._next_state_after_animation = WAIT_FOR_INPUT
        
        self.message_text = f"{msg} (Press SPACE to continue)"
        self.battle_state = ACTION_ANIMATION
    
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg")
        
        # 確保每次進入時，數據和顯示同步，特別是元素屬性
        my_mon = self.game_manager.bag._monsters_data[0] 
        enemy_mon = self.game_manager.bag._monsters_data[2]
        
        my_mon["element"] = get_element_from_sprite_path(my_mon['sprite_path'])
        enemy_mon["element"] = get_element_from_sprite_path(enemy_mon['sprite_path'])
        
        # 重新初始化顯示物件，確保是最新的 sprite 和 HP
        self.myPokemon = PokemonDisplay(
            sprite_path=f"assets/images/{my_mon['sprite_path']}",
            x=GameSettings.SCREEN_WIDTH // 10 - 30,
            y=GameSettings.SCREEN_HEIGHT * 3 // 4 - 20,
            hp_current=my_mon["hp"],
            hp_max=my_mon["max_hp"],
            level=my_mon["level"]
        )
        
        self.enemyPokemon = PokemonDisplay(
            sprite_path=f"assets/images/{enemy_mon['sprite_path']}",
            x=GameSettings.SCREEN_WIDTH * 6 // 10 - 30,
            y=GameSettings.SCREEN_HEIGHT // 10 - 20,
            hp_current=enemy_mon["hp"],
            hp_max=enemy_mon["max_hp"],
            level=enemy_mon["level"]
        )
        
        if self.pre_battle_check():
            return
            
        self.battle_state = WAIT_FOR_INPUT
        self.message_text = f"Battle started! You are {my_mon['element']}, Enemy is {enemy_mon['element']}. Select an action."
        
        # 確保等級被限制並存回
        lvl = clamp_level(self.game_manager.bag._monsters_data[0].get("level", 1))
        self.game_manager.bag._monsters_data[0]["level"] = lvl


    @override
    def update(self, dt: float) -> None:
        
        if self.battle_state == WAIT_FOR_INPUT:
            # ... (按鈕更新邏輯保持不變)
            self.attack_button.update(dt)
            self.run_button.update(dt)
            self.heal_button.update(dt)
            self.str_button.update(dt)
            self.def_button.update(dt)
            self.evolve_button.update(dt)
            
        elif self.battle_state == ENEMY_TURN:
            self.handle_enemy_turn_logic()
            
        elif self.battle_state == ACTION_ANIMATION:
            if input_manager.key_pressed(pg.K_SPACE):
                
                if self._next_state_after_animation == "RETURN_TO_MAP":
                    scene_manager.change_scene("game")
                    return

                if self.check_for_game_over(GAME_OVER):
                    return
                    
                if self._next_state_after_animation is not None:
                    self.battle_state = self._next_state_after_animation
                    if self.battle_state == WAIT_FOR_INPUT:
                        self.message_text = "It's your turn. Select an action."
                    self._next_state_after_animation = None
            
        elif self.battle_state == GAME_OVER:
            if input_manager.key_pressed(pg.K_SPACE):
                scene_manager.change_scene("game")

    @override
    def draw(self, screen: pg.Surface) -> None:
        # ... (繪圖邏輯保持不變)
        self.background.draw(screen)
        self.myPokemon.draw(screen)
        self.enemyPokemon.draw(screen) 
        
        screen.blit(self.menu_bg, self.menu_bg_rect)
        
        if self.battle_state == WAIT_FOR_INPUT:
            self.attack_button.draw(screen)
            self.run_button.draw(screen)
            self.heal_button.draw(screen)
            self.str_button.draw(screen)
            self.def_button.draw(screen)
            self.evolve_button.draw(screen)
        
        if self.battle_state == ACTION_ANIMATION or self.battle_state == GAME_OVER:
            screen.blit(self.message_box, self.message_box_rect)
            msg_surface = self.message_font.render(self.message_text, True, (255, 255, 255))
            msg_rect = msg_surface.get_rect(center=self.message_box_rect.center)
            screen.blit(msg_surface, msg_rect)
        
        elif self.battle_state == WAIT_FOR_INPUT:
            msg_surface = self.message_font.render(self.message_text, True, (0, 0, 0))
            msg_rect = msg_surface.get_rect(midtop=(self.menu_bg_rect.centerx, self.menu_bg_rect.top + 5))
            screen.blit(msg_surface, msg_rect)