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
    
    def get_layer_by_name(self, layer_name: str) -> list[int] | None:
        """
        根據圖層名稱從 TMX 數據中獲取該圖層的扁平化圖塊 GID 列表。
        
        Args:
            layer_name: 要尋找的圖層名稱 (例如 "PokemonBush")。
            
        Returns:
            list[int] | None: 如果找到，則返回 GID 列表；否則返回 None。
        """
        # 1. 透過名稱獲取 pytmx.TiledTileLayer 物件
        layer = self.tmxdata.get_layer_by_name(layer_name)
        
        if layer is None or not isinstance(layer, pytmx.TiledTileLayer):
            return None
        
        # 2. 從 TiledTileLayer 迭代器中提取 GID 並展平
        # TiledTileLayer 迭代器產生 (x, y, GID)
        # 我們只需要 GID，並且以行優先 (Row-major) 的順序收集它們。
        
        # 創建一個長度為 W*H 的列表，並初始化為 0
        map_width = self.tmxdata.width
        map_height = self.tmxdata.height
        
        # 使用列表生成式來確保順序正確 (從 tmxdata 獲取 GID 列表)
        # 注意: pytmx 提供的迭代器已經是行優先的
        
        # 獲取所有 (x, y, GID) 三元組
        gids: list[int] = [
            gid 
            for x, y, gid in layer.tiles()
        ]

        # 檢查尺寸是否正確 (W*H)
        if len(gids) != map_width * map_height:
             # 如果 TMX 格式不預期所有單元格都有 (x, y, GID) 數據，需要更嚴謹的填充
             # 但通常 for layer.tiles() 會返回所有單元格
             # 為了兼容性，我們可以使用 get_tile_gid(x, y) 逐一查詢
             
             # 更安全的做法 (逐一查詢 GID)：
             gids_safe: list[int] = []
             for y in range(map_height):
                 for x in range(map_width):
                     # pytmx.get_tile_gid(x, y, layer_index) 是最可靠的獲取方式
                     # 但由於我們已經有了 layer 物件，我們使用 layer.data 屬性 (它是一個二維陣列)
                     # 為了返回扁平化陣列，我們手動從 layer.data 構造:
                     try:
                         # 假設 layer.data 是一個二維列表 [y][x]
                         gids_safe.append(layer.data[y][x])
                     except:
                         # 處理 layer.data 不存在或格式不正確的情況
                         return gids # 嘗試返回迭代器獲取的 GIDs (如果存在)
             
             return gids_safe # 返回安全構造的扁平化列表
        
        # 如果迭代器工作正常，直接返回：
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
