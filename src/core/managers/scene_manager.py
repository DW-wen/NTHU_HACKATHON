import pygame as pg

from src.scenes.scene import Scene
from src.utils import Logger

class SceneManager:
    
    _scenes: dict[str, Scene]
    _current_scene: Scene | None = None
    _next_scene: str | None = None
    _previous_scene: Scene | None = None
    
    def __init__(self):
        Logger.info("Initializing SceneManager")
        self._scenes = {}
        
    def register_scene(self, name: str, scene: Scene) -> None:
        self._scenes[name] = scene
        
    def change_scene(self, scene_name: str) -> None:
        if scene_name in self._scenes:
            Logger.info(f"Changing scene to '{scene_name}'")
            self._next_scene = scene_name
        else:
            raise ValueError(f"Scene '{scene_name}' not found")
        
    @property
    def next_scene_name(self) -> str | None:
        """提供外部存取 _next_scene 的名稱"""
        return self._next_scene
    
    @property
    def current_scene(self) -> Scene | None:
        """提供外部存取 _current_scene 的 getter"""
        return self._current_scene
            
    def update(self, dt: float) -> None:
        # Handle scene transition
        if self._next_scene is not None:
            self._perform_scene_switch()
            
        # Update current scene
        if self._current_scene:
            self._current_scene.update(dt)
    
    # 改音量時要用的
    def handle_event(self, event: pg.event.EventType) -> None:
        """把事件傳給當前 scene"""
        if self._current_scene and hasattr(self._current_scene, "handle_event"):
            self._current_scene.handle_event(event)
            
    def draw(self, screen: pg.Surface) -> None:
    # 若是在 Setting Scene => 先畫上一個場景，再畫 SettingScene
    
        if (type(self._current_scene).__name__ in ("SettingScene", "BackpackScene")) and self._previous_scene:
            self._previous_scene.draw(screen)
            self._current_scene.draw(screen)
        else:
            if self._current_scene:
                self._current_scene.draw(screen)
            
    def _perform_scene_switch(self) -> None:
        if self._next_scene is None:
            return
            
        # Exit current scene
        if self._current_scene:
            self._current_scene.exit()
        
        self._previous_scene = self._current_scene
        
        self._current_scene = self._scenes[self._next_scene]
        
        # Enter new scene
        if self._current_scene:
            Logger.info(f"Entering {self._next_scene} scene")
            self._current_scene.enter()
            
        # Clear the transition request
        self._next_scene = None
    
    def close_overlay(self):
        """關閉 SettingScene 浮層，回到 previous_scene"""
        if (type(self._current_scene).__name__ in ("SettingScene", "BackpackScene")) and self._previous_scene:
            Logger.info("Closing overlay SettingScene")
            self._current_scene.exit()
            self._current_scene = self._previous_scene
            self._previous_scene = None
        