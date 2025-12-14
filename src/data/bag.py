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
        """Change the item count by delta. If item does not exist and delta>0, it will be created.
        If the resulting count <= 0 the item will be removed. Returns resulting count (0 if removed).
        """
        item = self.get_item_by_name(name)
        if item is None:
            if delta <= 0:
                return 0
            # create new item entry
            if sprite_path is None:
                sprite_path = ""
            item = {"name": name, "sprite_path": sprite_path, "count": delta}
            self._items_data.append(item)
            return item["count"]

        # modify existing
        new_count = item.get("count", 0) + delta
        if new_count <= 0:
            # remove
            try:
                self._items_data.remove(item)
            except ValueError:
                pass
            return 0

        item["count"] = new_count
        return new_count