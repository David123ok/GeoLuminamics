"""
File: creative_state.py
Creation Date: 2026-01-05
Description: Core state manager for the GeoLuminamics Creative Engine.
"""

from enum import Enum
from PySide6.QtGui import QColor

class CreativeStoneType(Enum):
    PRISM = 1
    MIRROR = 2
    SPLITTER = 3
    STOP = 4  # New stone type that absorbs lasers

import uuid

class CreativeStoneData:
    """Represents a stone's extended state in Creative Mode."""
    def __init__(self, stone_type=CreativeStoneType.PRISM, x=0, y=0):
        self.uid = str(uuid.uuid4())
        self.stone_type = stone_type
        self.x = x
        self.y = y
        self.rotation = 0.0
        
        # Extended Properties
        self.color = "#FFFFFF"  # Default white
        self.bloom_intensity = 1.0
        self.glow_intensity = 1.0
        self.rotation_speed = 0.0 # Degrees per frame/tick
        self.is_animating = False
        self.texture_path = None # Optional custom texture
        self.is_static = False   # If true, cannot be moved (lock)

    def to_dict(self):
        return {
            "type": self.stone_type.name,
            "x": self.x,
            "y": self.y,
            "rotation": self.rotation,
            "color": self.color,
            "bloom": self.bloom_intensity,
            "glow": self.glow_intensity,
            "rot_speed": self.rotation_speed,
            "anim": self.is_animating,
            "texture": self.texture_path,
            "static": self.is_static
        }

    @classmethod
    def from_dict(cls, data):
        stone = cls(
            CreativeStoneType[data["type"]],
            data["x"],
            data["y"]
        )
        stone.rotation = data.get("rotation", 0.0)
        stone.color = data.get("color", "#FFFFFF")
        stone.bloom_intensity = data.get("bloom", 1.0)
        stone.glow_intensity = data.get("glow", 1.0)
        stone.rotation_speed = data.get("rot_speed", 0.0)
        stone.is_animating = data.get("anim", False)
        stone.texture_path = data.get("texture")
        stone.is_static = data.get("static", False)
        return stone

class CreativeLaserData:
    """Represents a freeform laser source."""
    def __init__(self, x, y, direction_x, direction_y):
        self.uid = str(uuid.uuid4())
        self.x = x
        self.y = y
        self.direction = (direction_x, direction_y)
        self.color = "#FF0000" # Default Red
        self.intensity = 1.0
        self.bloom_intensity = 1.0
        self.glow_intensity = 1.0
        self.enabled = True
        # Animation
        self.is_animating = False
        self.rotation_speed = 0.0 # Degrees per frame
        
    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "dir_x": self.direction[0],
            "dir_y": self.direction[1],
            "color": self.color,
            "intensity": self.intensity,
            "bloom": self.bloom_intensity,
            "glow": self.glow_intensity,
            "enabled": self.enabled,
            "anim": self.is_animating,
            "rot_speed": self.rotation_speed
        }

    @classmethod
    def from_dict(cls, data):
        laser = cls(
            data["x"], data["y"],
            data["dir_x"], data["dir_y"]
        )
        laser.color = data.get("color", "#FF0000")
        laser.intensity = data.get("intensity", 1.0)
        laser.bloom_intensity = data.get("bloom", 1.0)
        laser.glow_intensity = data.get("glow", 1.0)
        laser.enabled = data.get("enabled", True)
        laser.is_animating = data.get("anim", False)
        laser.rotation_speed = data.get("rot_speed", 0.0)
        return laser

class CreativeState:
    """Manages the state of the Creative Engine."""
    
    def __init__(self, grid_size=39):
        self.grid_size = grid_size
        self.stones = [] # List of CreativeStoneData (positions are properties now, not keys)
        self.lasers = [] # List of CreativeLaserData
        self.background_color = "#1A1A1D"
        self.background_texture_path = None
        
        # Environment
        self.sky_color_top = "#1A1A1D"
        self.sky_color_bottom = "#1A1A1D" # If different, gradient
        self.sky_gradient_type = "radial"  # "linear" or "radial"
        self.sun_intensity = 1.0
        self.atmosphere_density = 0.0 # 0.0 to 1.0 (fog/overlay)
        self.atmosphere_color = "#FFFFFF"
        
    def add_stone(self, stone_type, x, y):
        """Add a new stone."""
        stone = CreativeStoneData(stone_type, x, y)
        self.stones.append(stone)
        return stone
        
    def remove_stone(self, stone):
        """Remove a stone object."""
        if stone in self.stones:
            self.stones.remove(stone)
            
    def get_stone_at(self, x, y):
        """Find stone at precise grid coordinates."""
        for stone in self.stones:
            if stone.x == x and stone.y == y:
                return stone
        return None

    def add_laser(self, x, y, dx, dy):
        """Add a freeform laser."""
        laser = CreativeLaserData(x, y, dx, dy)
        self.lasers.append(laser)
        return laser

    def remove_laser(self, laser):
        if laser in self.lasers:
            self.lasers.remove(laser)

    def clear(self):
        self.stones.clear()
        self.lasers.clear()

    def to_dict(self):
        return {
            "grid_size": self.grid_size,
            "bg_color": self.background_color,
            "bg_texture": self.background_texture_path,
            "sky_top": self.sky_color_top,
            "sky_bot": self.sky_color_bottom,
            "sky_grad": self.sky_gradient_type,
            "sun_int": self.sun_intensity,
            "atm_dens": self.atmosphere_density,
            "atm_col": self.atmosphere_color,
            "stones": [s.to_dict() for s in self.stones],
            "lasers": [l.to_dict() for l in self.lasers]
        }

    @classmethod
    def from_dict(cls, data):
        state = cls(data.get("grid_size", 39))
        state.background_color = data.get("bg_color", "#1A1A1D")
        state.background_texture_path = data.get("bg_texture")
        state.sky_color_top = data.get("sky_top", "#1A1A1D")
        state.sky_color_bottom = data.get("sky_bot", "#1A1A1D")
        state.sky_gradient_type = data.get("sky_grad", "radial")
        state.sun_intensity = data.get("sun_int", 1.0)
        state.atmosphere_density = data.get("atm_dens", 0.0)
        state.atmosphere_color = data.get("atm_col", "#FFFFFF")
        
        for s_data in data.get("stones", []):
            state.stones.append(CreativeStoneData.from_dict(s_data))
            
        for l_data in data.get("lasers", []):
            state.lasers.append(CreativeLaserData.from_dict(l_data))
            
        return state
