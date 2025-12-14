from typing import Dict, Any, Optional
import random

# Assuming these are available in the path
from src.scenes.battle_scene.evolution_data import next_evolution_info, next_evolution 
from src.utils import Logger
from src.scenes.battle_scene.element_data import get_element_from_sprite_path, elemental_damage_bonus

# Fallback implementation if import fails
try:
    from src.utils.definition import clamp_level
except ImportError:
    def clamp_level(level: int) -> int:
        lv = int(level) if isinstance(level, int) else 1
        return max(1, min(3, lv))
        
# Fallback for next_evolution (should be defined in evolution_data.py)
try:
    from src.scenes.battle_scene.evolution_data import next_evolution
except ImportError:
    def next_evolution(name: str) -> str | None:
        if name == "menusprite1.png": return "menusprite2.png"
        if name == "menusprite2.png": return "menusprite3.png"
        return None


class BattleLogic:
    """
    A class dedicated to handling core battle calculations, buff management, 
    and evolution logic, separated from Pygame/Scene concerns.
    """
    def __init__(self, game_manager: Any, player_index: int = 0, enemy_index: int = 2):
        self.game_manager = game_manager
        # Allow different scenes to use different indices for player/enemy
        self.player_index = player_index
        self.enemy_index = enemy_index
        # Buff state managed here
        self.player_attack_buff = 0
        self.player_attack_buff_turns = 0
        self.player_defense_buff = 0
        self.player_defense_buff_turns = 0

    def _get_pokemon_data(self, is_player: bool) -> Dict[str, Any]:
        """Retrieves player or enemy Pokémon data using configured indices."""
        index = self.player_index if is_player else self.enemy_index
        try:
            return self.game_manager.bag._monsters_data[index]
        except IndexError:
            Logger.error(f"Missing Pokémon data at index {index}")
            return {}

    def apply_buff_turn_end(self, is_player_turn: bool):
        """Decrements buff duration at the end of a turn."""
        if is_player_turn:
            if self.player_defense_buff_turns > 0:
                self.player_defense_buff_turns -= 1
                if self.player_defense_buff_turns == 0:
                    self.player_defense_buff = 0
        else: # Enemy turn end (player attack turn end)
             if self.player_attack_buff_turns > 0: 
                self.player_attack_buff_turns -= 1
                if self.player_attack_buff_turns == 0:
                    self.player_attack_buff = 0

    def calculate_player_attack_damage(self) -> tuple[int, int, str]:
        """
        Calculates the player's attack damage.
        Returns (total damage, elemental bonus, attacker element).
        """
        player_mon = self._get_pokemon_data(is_player=True)
        enemy_mon = self._get_pokemon_data(is_player=False)
        
        base_damage = 20
        damage = base_damage + self.player_attack_buff
        
        attacker_elem = player_mon.get("element")
        defender_elem = enemy_mon.get("element")
        
        bonus = elemental_damage_bonus(attacker_elem, defender_elem)
        damage += bonus
        
        # Consume Attack Buff (handled here for clarity, even if BattleScene calls it)
        self.apply_buff_turn_end(is_player_turn=False)

        return damage, bonus, attacker_elem
        
    def calculate_enemy_attack_damage(self) -> tuple[int, int, str]:
        """
        Calculates the enemy's attack damage.
        Returns (total damage, elemental bonus, attacker element).
        """
        player_mon = self._get_pokemon_data(is_player=True)
        enemy_mon = self._get_pokemon_data(is_player=False)

        damage = random.randint(15, 25)
        
        attacker_elem = enemy_mon.get("element")
        defender_elem = player_mon.get("element")
        
        bonus = elemental_damage_bonus(attacker_elem, defender_elem)
        damage += bonus
        
        # Apply Defense Buff
        if self.player_defense_buff_turns > 0:
            damage = max(0, damage - self.player_defense_buff)
        
        # Consume Defense Buff (handled here for clarity, even if BattleScene calls it)
        self.apply_buff_turn_end(is_player_turn=True)

        return damage, bonus, attacker_elem
    
    def apply_item_effect(self, item_name: str) -> tuple[str, bool]:
        """
        Applies item effects.
        Returns (message, success_status)
        """
        my_mon = self._get_pokemon_data(is_player=True)
        if not my_mon: return ("Failed to retrieve Pokémon data.", False)
        
        item = self.game_manager.bag.get_item_by_name(item_name)
        if item is None or item.get("count", 0) <= 0:
            return (f"No {item_name} left!", False)
            
        self.game_manager.bag.change_item_count(item_name, -1)
        
        if item_name == "Heal":
            heal_amt = 30
            current_hp = my_mon.get("hp", 0)
            max_hp = my_mon.get("max_hp", 100)
            new_hp = min(max_hp, current_hp + heal_amt)
            healed = new_hp - current_hp
            my_mon["hp"] = new_hp
            return (f"Used Heal! Recovered {healed} HP.", True)

        elif item_name == "Attack":
            self.player_attack_buff = 10
            self.player_attack_buff_turns = 2 
            return ("Used Attack! Next two attacks are stronger.", True)

        elif item_name == "Defense":
            self.player_defense_buff = 10
            self.player_defense_buff_turns = 2 
            return ("Used Defense! Next two enemy attacks reduced.", True)
        
        return ("Unknown item effect.", False)


    def try_evolve_pokemon(self) -> tuple[str, bool]:
        """Attempts to evolve the player's Pokémon, with level constraints."""
        p = self._get_pokemon_data(is_player=True)
        if not p: return ("Failed to retrieve Pokémon data.", False)

        current_level = p.get("level", 1)
        name = p.get("sprite_path", "")

        # Use next_evolution_info to check if the current level is sufficient to trigger the next evolution.
        evolution_info = next_evolution_info(name, current_level)
        
        # --- REMOVED HARD LIMIT CHECK FOR current_level >= 4 ---

        if evolution_info is None:
            # 1. Check if there is a next form at all (using the old function for simple existence check)
            if next_evolution(name) is None:
                # If there is no next form, it's the final stage.
                return ("Cannot evolve, already at final form.", False)
            
            # 2. If there IS a next form, but evolution_info is None, it means the current level is insufficient.
            # We must determine the required level. Since next_evolution_info handles the actual check, 
            # we must rely on the configuration data to know the requirement.
            
            # Since evolution_info failed, we try to deduce the *required* level from the next form's entry.
            # A cleaner solution would be to get the required_level from evolution_data directly.
            
            # Fallback deduction for messaging:
            # Since next_evolution_info failed, we know current_level < required_level.
            # We attempt to find the next required level from the data for better messaging.
            
            next_sprite = next_evolution(name)
            # This relies on accessing the private dictionary or providing a public helper in evolution_data
            try:
                # Assuming _EVOLUTIONS is accessible or we have a dedicated helper
                from src.scenes.battle_scene.evolution_data import _EVOLUTIONS
                evolution_data = _EVOLUTIONS.get(name)
                
                if evolution_data:
                    required_level_display = evolution_data[1]
                else:
                    required_level_display = current_level + 1 # Safe default if lookup fails
            except (ImportError, KeyError):
                required_level_display = current_level + 1

            return (f"Evolution failed: Requires Level {required_level_display} to evolve.", False)


        # Evolution conditions met (current level is >= the required minimum level)
        next_sprite, required_level_check, next_level = evolution_info

        # Execute evolution
        p["level"] = next_level
        p["max_hp"] = p["max_hp"] + 50 
        p["hp"] = p["max_hp"] # Fully heals on evolution
        
        old = p.get("sprite_path", "")
        folder = "/".join(old.split("/")[:-1])
        p["sprite_path"] = (folder + "/" if folder else "") + next_sprite

        # Update element based on new sprite
        p["element"] = get_element_from_sprite_path(p['sprite_path'])

        return ("Evolution successful!", True)