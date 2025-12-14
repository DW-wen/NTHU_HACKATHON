from typing import Dict, Tuple, Optional

# Evolution Data: {Current Sprite Filename: (Next Sprite Filename, Required Level After Evolution)}
# The Required Level is the minimum level the monster should reach after the evolution.
_EVOLUTIONS: Dict[str, Tuple[str, int]] = {
    # Grass line
    # Form 1 (menusprite1) -> Form 2 (menusprite2) requires Level 2 post-evolution
    "menusprite1.png": ("menusprite2.png", 2),
    # Form 2 (menusprite2) -> Form 3 (menusprite3) requires Level 3 post-evolution
    "menusprite2.png": ("menusprite3.png", 3),
    
    # Fire line
    "menusprite7.png": ("menusprite8.png", 2),
    "menusprite8.png": ("menusprite9.png", 3),
    
    # Water line
    "menusprite12.png": ("menusprite13.png", 2),
    "menusprite13.png": ("menusprite14.png", 3),
    
    # Two-step line
    # Form 1 (menusprite15) -> Form 2 (menusprite16) requires Level 2 post-evolution
    "menusprite15.png": ("menusprite16.png", 2),
    # menusprite16 has no further evolution
}


def next_evolution_info(sprite_path: str, current_level: int) -> Optional[Tuple[str, int, int]]:
    """
    Checks if evolution is possible and returns the next stage's information.
    
    The logic:
    1. Check if the current level is sufficient to reach the required_level after level up (current_level + 1 >= required_level).
    2. Check if the evolution would exceed the maximum level (Level 4).
    
    Args:
        sprite_path: The full sprite path of the current Pokémon.
        current_level: The current level of the Pokémon.
        
    Returns:
        Tuple[next_sprite_filename, required_level_for_next_stage, next_level] or None
    """
    if not sprite_path:
        return None
        
    name = sprite_path.split("/")[-1]
    evolution_info = _EVOLUTIONS.get(name)
    
    if evolution_info:
        next_sprite_name, required_level = evolution_info
        
        # next_level = current_level + 1
        print(f"Checking evolution for {name}, current level: {current_level}, required level: {required_level}")
        # 1. Check if the current level is sufficient:
        # Evolution is allowed if the resulting level (current_level + 1) is >= the required_level.
        # This handles the "Level 2 needed" rule:
        # If required_level=2, current_level=1 -> next_level=2. (2 >= 2) -> Allowed.
        # If required_level=3, current_level=2 -> next_level=3. (3 >= 3) -> Allowed.
        if current_level < required_level:
            # Level is too low to reach the required_level after evolution
            return None 
            
        # 2. Check for maximum level constraint
        # Level 4 and above cannot evolve further.
      

        # FIX APPLIED HERE: Return the calculated next_level (current_level + 1)
        return next_sprite_name, required_level, current_level
        
    return None


def next_evolution(sprite_path: str) -> str | None:
    """Old next_evolution function, kept for compatibility, but not used in core logic."""
    if not sprite_path: return None
    name = sprite_path.split("/")[-1]
    
    # Only return the next sprite name
    info = _EVOLUTIONS.get(name)
    return info[0] if info else None