import pygame as pg

from saves.load_data import load_save
from src.core.managers.game_manager import GameManager
from src.scenes.backpack_scene import BackpackScene
from src.scenes.battle_scene.battle_scene import BattleScene
from src.scenes.battle_scene.catch_scene import CatchScene
from src.scenes.setting_scene import SettingScene
from src.scenes.shop_scene.shop_scene import ShopScene
from src.utils import GameSettings, Logger
from .services import scene_manager, input_manager


from src.scenes.menu_scene import MenuScene
from src.scenes.game_scene import GameScene

class Engine:

    screen: pg.Surface              # Screen Display of the Game
    clock: pg.time.Clock            # Clock for FPS control
    running: bool                   # Running state of the game

    def __init__(self):
        Logger.info("Initializing Engine")

        pg.init()

        self.screen = pg.display.set_mode((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        self.clock = pg.time.Clock()
        self.running = True

        pg.display.set_caption(GameSettings.TITLE)
        
        from src.data.bag import Bag
        
        gm = GameManager.load("saves/game0.json") 
            
        if gm is None:
                # 如果載入失敗，才使用 minimal_gm 進行「最小化」初始化
                # 但你必須提供一個有效的 start_map 鍵
                Logger.error("Failed to load game save. Using minimal fallback.")
                from src.data.bag import Bag
                
                # **重點：這裡的 start_map 不能是空字串！**
                # 根據 game0.json，你的起始地圖是 "map.tmx"
                start_map_key = "map.tmx" 
                
                # 你需要建立 Map 實例並將其放入 maps 字典中，以便 GameManager 正常工作
                # 但因為你沒有提供 Map 的類別程式碼，這裡先假設它能被建立
                # 為了避免這個 KeyError，我們必須確保 start_map_key 存在於 enemy_trainers 字典中
                
                minimal_gm = GameManager(
                    maps={}, 
                    start_map=start_map_key, # 必須是一個有效的鍵
                    player=None, 
                    # 至少要為起始地圖提供一個空的訓練師列表
                    enemy_trainers={start_map_key: []}, 
                    bag=Bag([], [])
                )
                gm = minimal_gm
            
            # 2. 使用正確載入或初始化的 gm 註冊場景
        scene_manager.register_scene("menu", MenuScene())
        scene_manager.register_scene("game", GameScene(gm)) # 使用 gm
        scene_manager.register_scene("setting", SettingScene(gm))
        scene_manager.register_scene("backpack", BackpackScene(gm))
        scene_manager.register_scene("battle", BattleScene(gm))
        scene_manager.register_scene("catch", CatchScene(gm))
        scene_manager.register_scene("shop", ShopScene(gm))
        '''
        [TODO HACKATHON 5]
        Register the setting scene here
        '''
        scene_manager.change_scene("menu")

    def run(self):
        Logger.info("Running the Game Loop ...")

        while self.running:
            dt = self.clock.tick(GameSettings.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()

    def handle_events(self):
        input_manager.reset()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            input_manager.handle_events(event)
            scene_manager.handle_event(event)
            

    def update(self, dt: float):
        scene_manager.update(dt)

    def render(self):
        self.screen.fill((0, 0, 0))     # Make sure the display is cleared
        scene_manager.draw(self.screen) # Draw the current scene
        pg.display.flip()               # Render the display
