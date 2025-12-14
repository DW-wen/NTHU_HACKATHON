# catch_scene.py

from typing import override
import pygame as pg

# 假設 BattleScene 和 CaptureLogic 已在導入路徑中
from .battle_scene import BattleScene, SimpleTextButton, GameManager, WAIT_FOR_INPUT, GAME_OVER, ACTION_ANIMATION, ENEMY_TURN

from .capture_logic import CaptureLogic 

class CatchScene(BattleScene):
    """
    捕捉場景：繼承自 BattleScene，並添加捕捉按鈕和邏輯。
    """
    
    # 捕捉特有的屬性
    pokeball_count: int 
    capture_system: CaptureLogic
    catch_button: SimpleTextButton # 捕捉按鈕現在只屬於 CatchScene

    @override
    def __init__(self, game_manager: GameManager):
        # 呼叫父類的初始化，設置所有通用的戰鬥 UI、Pokémon 實例和 Attack/Run 按鈕
        super().__init__(game_manager) 
        
        # --- 捕捉專屬初始化 ---
        
        # 1. 初始化 CaptureLogic
        # 由於 _get_pokeball_count 屬於 CatchScene，我們可以在這裡使用它
        initial_pokeball_count = self._get_pokeball_count("Pokeball")
        self.capture_system = CaptureLogic(self.game_manager, initial_pokeball_count)
        self.pokeball_count = self.capture_system.pokeball_count
        
        # 2. 設置 Catch Button (繼承了父類的 UI 屬性，如 menu_bg_rect)
        button_width = 150
        button_height = 50
        padding = 50
        
        # 計算 Catch Button 的位置 (位於 Attack 和 Run 之間)
        catch_rect = pg.Rect(
            self.menu_bg_rect.left + padding + button_width + padding, 
            self.menu_bg_rect.centery - button_height // 2, 
            button_width, 
            button_height
        )
        self.catch_button = SimpleTextButton(
            text="Catch", 
            rect=catch_rect,
            on_click=self.handle_catch,
            font_size=28,
            text_color=(0, 0, 0),
            default_color=(255, 255, 255, 0), 
            hover_color=(220, 220, 220, 150)
        )
        
    def _get_pokeball_count(self, item_name: str = "Pokeball") -> int:
        """從 GameManager 的背包中尋找特定物品（預設為 Pokeball）的數量。（僅用於初始化）"""
        for item in self.game_manager.bag._items_data:
            if item.get("name", "").lower() == item_name.lower():
                return item.get("count", 0) 
        return 0

    def handle_catch(self):
        """處理 Catch 按鈕點擊 - 使用 CaptureLogic 嘗試捕捉敵方 Pokémon。"""
        if self.battle_state != WAIT_FOR_INPUT:
            return
            
        # 呼叫獨立的捕捉邏輯
        new_message, next_battle_state = self.capture_system.attempt_capture()
        
        # 更新場景狀態和訊息
        self.message_text = new_message
        self.battle_state = next_battle_state
        
        # 同步場景內的球數
        self.pokeball_count = self.capture_system.pokeball_count
        
        if next_battle_state == "RETURN_TO_MAP":
            self._next_state_after_animation = "RETURN_TO_MAP"
        else:
            # 設置為 ENEMY_TURN, WAIT_FOR_INPUT 或 GAME_OVER
            self._next_state_after_animation = next_battle_state 
            
        # 進入動畫狀態 (等待 SPACE 鍵確認)
        self.battle_state = ACTION_ANIMATION
        
        

    @override
    def update(self, dt: float) -> None:
        """
        覆寫 update 方法以處理 Catch Button 的更新。
        父類 BattleScene.update 處理了所有通用的狀態切換。
        """
        # 讓父類處理大部分邏輯
        super().update(dt)
        
        # 只有在等待輸入時，才額外更新 Catch Button
        if self.battle_state == WAIT_FOR_INPUT:
            self.catch_button.update(dt)

    @override
    def draw(self, screen: pg.Surface) -> None:
        """
        覆寫 draw 方法以繪製 Catch Button。
        父類 BattleScene.draw 處理了所有通用的繪製。
        """
        # 讓父類繪製背景、Pokémon、Attack 和 Run 按鈕等
        super().draw(screen)
        
        # 在等待輸入時，額外繪製 Catch Button
        if self.battle_state == WAIT_FOR_INPUT:
            self.catch_button.draw(screen)