# capture_logic.py

import random
from typing import TYPE_CHECKING
# 這裡需要引用 GameManager，但由於 GameManager 可能尚未完全定義
# 我們使用 TYPE_CHECKING 來避免循環引用，並使用註釋來指定類型。
if TYPE_CHECKING:
    from src.core.managers.game_manager import GameManager
    
# 定義戰鬥狀態常數 (確保在 CatchScene 和此處定義一致)
ACTION_ANIMATION = "ACTION_ANIMATION"
GAME_OVER = "GAME_OVER"
WAIT_FOR_INPUT = "WAIT_FOR_INPUT"
ENEMY_TURN = "ENEMY_TURN"

class CaptureLogic:
    """
    處理捕捉寶可夢的專門邏輯。
    需要 GameManager 存取背包和隊伍資料。
    """
    
    # 隊伍最大容量
    MAX_POKEMON_COUNT: int = 5
    
    def __init__(self, game_manager: 'GameManager', pokeball_count: int):
        self.game_manager = game_manager
        # 暫時在邏輯層保存球的數量，執行後再寫回 bag
        self.pokeball_count = pokeball_count 

    def _get_pokeball_count(self, item_name: str = "Pokeball") -> int:
        """從 GameManager 的背包中尋找特定物品的數量。"""
        for item in self.game_manager.bag._items_data:
            if item.get("name", "").lower() == item_name.lower():
                return item.get("count", 0) 
        return 0

    def _update_pokeball_count_in_bag(self, item_name: str = "Pokeball"):
        """將 self.pokeball_count 的最新值寫回 GameManager.bag._items_data。"""
        for item in self.game_manager.bag._items_data:
            if item.get("name", "").lower() == item_name.lower():
                item["count"] = self.pokeball_count
                return
    
    def attempt_capture(self) -> tuple[str, str]: # 保持回傳 (訊息, 狀態)
        """執行捕捉流程，回傳 (新的 message_text, 下一個狀態)。"""
        
        # 1. 隊伍容量檢查
        if len(self.game_manager.bag._monsters_data) >= self.MAX_POKEMON_COUNT:
            new_message = f"You already have {self.MAX_POKEMON_COUNT} Pokémon! Catch failed. (Press SPACE to continue)"
            # 狀態應返回等待輸入
            return new_message, WAIT_FOR_INPUT
            
        # 2. 球的數量檢查
        if self.pokeball_count <= 0:
            new_message = "You are out of Poké Balls! (Press SPACE to continue)"
            # 狀態應返回等待輸入
            return new_message, WAIT_FOR_INPUT
            
        # 3. 消耗資源 (扣除球)
        self.pokeball_count -= 1
        self._update_pokeball_count_in_bag("Pokeball")
        
        # 4. 捕捉機率判定
        if random.randint(1, 100) <= 50:
            # 捕捉成功邏輯 (與上次修正相同)
            try:
              
                self.game_manager.bag._monsters_data.append(self.game_manager.bag._monsters_data[1])
            except IndexError:
                pass 
            
            new_message = f"Successfully caught the Pokémon! (Balls left: {self.pokeball_count}) (Press SPACE to return)"
            # 捕捉成功，戰鬥結束
            return new_message, "RETURN_TO_MAP" # 使用 RETURN_TO_MAP 標記，以便在 CatchScene 中設置
            
        else:
            # 捕捉失敗 (切換到下一回合/返回等待輸入)
            new_message = f"The Pokémon broke free! (Balls left: {self.pokeball_count}) (Press SPACE to continue)"
            # 失敗視為消耗玩家回合，應該切換到敵方回合
            return new_message, ENEMY_TURN # 確保 ENEMY_TURN 被導入