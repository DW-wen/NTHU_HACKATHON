import pygame as pg
import json
from src.utils import GameSettings
from src.utils.definition import Monster, Item


class Bag:
    _monsters_data: list[Monster]
    _items_data: list[Item]

    def __init__(self, monsters_data: list[Monster] | None = None, items_data: list[Item] | None = None):
        self._monsters_data = monsters_data if monsters_data else []
        self._items_data = items_data if items_data else []

    def update(self, dt: float):
        pass

    def draw(self, screen: pg.Surface):
        pass

    def to_dict(self) -> dict[str, object]:
        return {
            "monsters": list(self._monsters_data),
            "items": list(self._items_data)
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Bag":
        monsters = data.get("monsters") or []
        # Ensure monster levels are clamped to supported range
        from src.utils.definition import clamp_level
        for m in monsters:
            if isinstance(m, dict) and "level" in m:
                try:
                    m["level"] = clamp_level(m["level"])
                except Exception:
                    m["level"] = 1
        items = data.get("items") or []
        bag = cls(monsters, items)
        return bag

    # --- Convenience helpers for Shop interactions ---
    def get_item_by_name(self, name: str) -> dict | None:
        for it in self._items_data:
            if it.get("name") == name:
                return it
        return None

    def change_item_count(self, name: str, delta: int, sprite_path: str | None = None) -> int:
        item = self.get_item_by_name(name)
        if item is None:
            if delta <= 0:
                return 0
            # create new item entry
            if sprite_path is None:
                sprite_path = ""
            item = {"name": name, "sprite_path": sprite_path, "count": delta}
            self._items_data.append(item)
            new_count = item["count"]
            # notify scenes that bag changed
            try:
                from src.core.services import scene_manager
                for sc in (scene_manager.current_scene, getattr(scene_manager, "_previous_scene", None)):
                    if sc is None:
                        continue
                    if hasattr(sc, "_initialize_displays"):
                        sc._initialize_displays()
                    if hasattr(sc, "backpack_items"):
                        for b in sc.backpack_items:
                            bag_item = self.get_item_by_name(b.name)
                            qty = bag_item.get("count", 0) if bag_item is not None else 0
                            b.set_quantity(qty)
                    if hasattr(sc, "item_displays"):
                        for idisp in sc.item_displays:
                            bag_item = self.get_item_by_name(idisp.name)
                            qty = bag_item.get("count", 0) if bag_item is not None else 0
                            idisp.set_quantity(qty)
            except Exception:
                pass
            return new_count

        # modify existing
        new_count = item.get("count", 0) + delta
        # Keep item in bag even if count reaches 0 (per requirement)
        if new_count <= 0:
            item["count"] = 0
        else:
            item["count"] = new_count

        # notify scenes that bag changed
        try:
            from src.core.services import scene_manager
            for sc in (scene_manager.current_scene, getattr(scene_manager, "_previous_scene", None)):
                if sc is None:
                    continue
                if hasattr(sc, "_initialize_displays"):
                    sc._initialize_displays()
                if hasattr(sc, "backpack_items"):
                    for b in sc.backpack_items:
                        bag_item = self.get_item_by_name(b.name)
                        qty = bag_item.get("count", 0) if bag_item is not None else 0
                        b.set_quantity(qty)
                if hasattr(sc, "item_displays"):
                    for idisp in sc.item_displays:
                        bag_item = self.get_item_by_name(idisp.name)
                        qty = bag_item.get("count", 0) if bag_item is not None else 0
                        idisp.set_quantity(qty)
        except Exception:
            pass

        return item["count"]