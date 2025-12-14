import pygame as pg
import pytmx

from src.utils import load_tmx, Position, GameSettings, PositionCamera, Teleport

class Map:
    # Map Properties
    path_name: str
    tmxdata: pytmx.TiledMap
    # Position Argument
    spawn: Position
    teleporters: list[Teleport]
    # Rendering Properties
    _surface: pg.Surface
    _collision_map: list[pg.Rect]

    def __init__(self, path: str, tp: list[Teleport], spawn: Position):
        self.path_name = path
        self.tmxdata = load_tmx(path)
        self.spawn = spawn
        self.teleporters = tp

        pixel_w = self.tmxdata.width * GameSettings.TILE_SIZE
        pixel_h = self.tmxdata.height * GameSettings.TILE_SIZE

        # Prebake the map
        self._surface = pg.Surface((pixel_w, pixel_h), pg.SRCALPHA)
        self._render_all_layers(self._surface)
        # Prebake the collision map
        self._collision_map = self._create_collision_map()

    def update(self, dt: float):
        return
    

    # 假設 pytmx 已經被導入

    def get_layer_by_name(self, layer_name: str) -> list[int] | None:
        """
        根據圖層名稱從 TMX 數據中獲取該圖層的扁平化圖塊 GID 列表。
        
        Args:
            layer_name: 要尋找的圖層名稱 (例如 "PokemonBush")。
            
        Returns:
            list[int] | None: 如果找到，則返回 GID 列表；否則返回 None。
        """
        try:
            # 1. 透過名稱獲取 pytmx.TiledLayer 物件
            layer = self.tmxdata.get_layer_by_name(layer_name)
        except ValueError:
            # 解決 Layer not found 的錯誤 (例如 "PokemonBush" 不存在時)
            # 這是您程式碼最需要修改的地方。
            # print(f"Layer '{layer_name}' not found in map data.") # 使用 Logger.info/warning 更好
            return None

        # 2. 檢查圖層類型：必須是 TiledTileLayer 才能有圖塊 GID 數據
        if not isinstance(layer, pytmx.TiledTileLayer):
            # print(f"Layer '{layer_name}' found, but it is not a Tile Layer.")
            return None

        # 3. 從 TiledTileLayer 的 .data 屬性中高效獲取 GID 並展平
        # layer.data 是一個二維列表 (Row-major: [y][x])，包含所有 GID (包括 0)
        
        gids: list[int] = []
        # 逐行迭代並將其展平 (flatten)
        for row in layer.data:
            gids.extend(row)
            
        # 檢查尺寸是否正確 (這通常是多餘的，因為 layer.data 已經保證尺寸為 W*H)
        map_size = self.tmxdata.width * self.tmxdata.height
        if len(gids) != map_size:
            # 雖然不應該發生，但如果發生則發出警告
            print(f"Warning: Flattened GID list size ({len(gids)}) does not match expected map size ({map_size}).")
            
        return gids

    def draw(self, screen: pg.Surface, camera: PositionCamera):
        screen.blit(self._surface, camera.transform_position(Position(0, 0)))
        
        # Draw the hitboxes collision map
        if GameSettings.DRAW_HITBOXES:
            for rect in self._collision_map:
                pg.draw.rect(screen, (255, 0, 0), camera.transform_rect(rect), 1)
        
    def check_collision(self, rect: pg.Rect) -> bool:
        
        for collision_rec in self._collision_map:
            if rect.colliderect(collision_rec):
                return True
       
        return False
        
    def check_teleport(self, pos: Position) -> Teleport | None:
        '''[TODO HACKATHON 6] 
        Teleportation: Player can enter a building by walking into certain tiles defined inside saves/*.json, and the map will be changed
        Hint: Maybe there is an way to switch the map using something from src/core/managers/game_manager.py called switch_... 
        '''
        for tp in self.teleporters:
            grid_x = pos.x // GameSettings.TILE_SIZE
            grid_y = pos.y // GameSettings.TILE_SIZE
            tp_x = tp.pos.x // GameSettings.TILE_SIZE
            tp_y = tp.pos.y // GameSettings.TILE_SIZE
            if grid_x == tp_x and grid_y == tp_y:
                return tp 
            
        return None

    def _render_all_layers(self, target: pg.Surface) -> None:
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self._render_tile_layer(target, layer)
            # elif isinstance(layer, pytmx.TiledImageLayer) and layer.image:
            #     target.blit(layer.image, (layer.x or 0, layer.y or 0))
 
    def _render_tile_layer(self, target: pg.Surface, layer: pytmx.TiledTileLayer) -> None:
        for x, y, gid in layer:
            if gid == 0:
                continue
            image = self.tmxdata.get_tile_image_by_gid(gid)
            if image is None:
                continue

            image = pg.transform.scale(image, (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
            target.blit(image, (x * GameSettings.TILE_SIZE, y * GameSettings.TILE_SIZE))
    
    def _create_collision_map(self) -> list[pg.Rect]:
        rects = []
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and ("collision" in layer.name.lower() or "house" in layer.name.lower()):
                for x, y, gid in layer:
                    if gid != 0:
                        '''
                        [TODO HACKATHON 4]
                        rects.append(pg.Rect(...))
                        Append the collision rectangle to the rects[] array
                        Remember scale the rectangle with the TILE_SIZE from settings
                        '''
                        rects.append(
                            pg.Rect(
                                x * GameSettings.TILE_SIZE,
                                y * GameSettings.TILE_SIZE,
                                GameSettings.TILE_SIZE,
                                GameSettings.TILE_SIZE
                                
                            )
                        )
                        pass
        return rects

    @classmethod
    def from_dict(cls, data: dict) -> "Map":
        tp = [Teleport.from_dict(t) for t in data["teleport"]]
        pos = Position(data["player"]["x"] * GameSettings.TILE_SIZE, data["player"]["y"] * GameSettings.TILE_SIZE)
        return cls(data["path"], tp, pos)

    def to_dict(self):
        return {
            "path": self.path_name,
            "teleport": [t.to_dict() for t in self.teleporters],
            "player": {
                "x": self.spawn.x // GameSettings.TILE_SIZE,
                "y": self.spawn.y // GameSettings.TILE_SIZE,
            }
        }
