from typing import Dict

# ----------------- 元素邏輯數據 -----------------

SPRITE_ELEMENT_MAP: Dict[str, str] = {
    "menusprite1.png": "Grass",
    "menusprite2.png": "Grass",
    "menusprite3.png": "Grass",
    "menusprite15.png": "Grass",
    "menusprite16.png": "Grass",
    "menusprite7.png": "Fire",
    "menusprite8.png": "Fire",
    "menusprite9.png": "Fire",
    "menusprite12.png": "Water",
    "menusprite13.png": "Water",
    "menusprite14.png": "Water",
    "menusprite4.png": "Normal",
    "menusprite5.png": "Normal",
    "menusprite6.png": "Normal",
    "menusprite10.png": "Normal",
    "menusprite11.png": "Normal",
}

# 定義元素克制關係： Key 剋制 Value
_ELEMENTAL_STRENGTH: Dict[str, str] = {
    "Water": "Fire",
    "Fire": "Grass",
    "Grass": "Water",
}

# ----------------- 元素輔助函數 -----------------

def get_element_from_sprite_path(sprite_path: str) -> str:
    """根據 sprite path 回傳元素，預設為 Normal。"""
    # 提取檔名
    filename = sprite_path.split("/")[-1]
    return SPRITE_ELEMENT_MAP.get(filename, "Normal")


def elemental_damage_bonus(attacker_element: str | None, defender_element: str | None) -> int:
    """Return additional flat damage if attacker element is strong against defender.
    Returns +10 for super effective, -5 for not very effective, and 0 otherwise.
    """
    try:
        if not attacker_element or not defender_element:
            return 0
            
        attacker = attacker_element.capitalize()
        defender = defender_element.capitalize()
        
        # Super Effective: +10 damage (Attacker強於Defender)
        if _ELEMENTAL_STRENGTH.get(attacker) == defender:
            return 10
            
        # Not Very Effective: -5 damage (Defender強於Attacker)
        if _ELEMENTAL_STRENGTH.get(defender) == attacker:
            return -5
            
    except Exception:
        pass
    return 0