"""
World module for the RPG game.
Handles map loading, collision rects, hazard rects, and pyscroll group.
"""

from cmath import rect
from logging import exception
import pygame
from pygame.surfarray import pixels_alpha
import pytmx
import pyscroll
from pathlib import Path
import camera
from globals import SCREEN_WIDTH, SCREEN_HEIGHT

class World:
    """Loads and manages the game map, collision, and hazard rects."""
    def __init__(self, tmx_path, player, zoom=3.0, default_layer=8):
        self.map_layer = None
        self.map_width = 0 
        self.map_height = 0 
        self.collision_rects = [] 
        self.hazard_rects = []
        self.doors = []
        self.group = None
        self.zoom = zoom

        tmx_data = pytmx.load_pygame(str(tmx_path), pixelalpha=True)

        map_data = pyscroll.data.TiledMapData(tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(
            map_data,
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.map_layer.zoom = zoom
        self.map_width = tmx_data.width * tmx_data.tilewidth
        self.map_height = tmx_data.height * tmx_data.tileheight

        # Load collision, hazard and door rects
        for obj in tmx_data.objects:
            if obj.x is not None:
                try:
                    rect = pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))
                    name = (obj.name or "").lower()
                    if name == "hazard":
                        self.hazard_rects.append(rect)
                    elif name == "door":
                        self.doors.append({
                            "rect": rect,
                            "open": False,
                            "id": obj.properties.get("id", 0)
                        })
                    else:
                        self.collision_rects.append(rect)
                except Exception:
                    pass

        # Pyscroll group for z-ordering
        self.group = pyscroll.PyscrollGroup(
            map_layer=self.map_layer,
            default_layer=self.default_layer
        )
        self.group.add()

    def get_collision_rects(self):
        """Return collision rects plus any closed doors."""
        closed_doors = [d["rect"] for d in self.doors if not d[open]]
        return self.collision_rects + closed_doors

    def check_collision(self, player_rect, old_x, old_y, player):
        """Check wall and closed door collision."""
        for rect in self.get_collision_rects():
            if player_rect.colliderect(rect):
                player.position.x = old_x
                player.position.y = old_y
                break
    
    def check_hazard(self, player_rect, player, dt):
        """Check hazard collision and apply damage."""
        for rect in self.hazard_rects:
            if player_rect.colliderect(rect):
                player.take_damage(10)
                break
    
    def get_nearby_door(self, player):
        """Return the nearest closed door if player is close enough."""
        for door in self.doors:
            if door["open"]:
                continue
        interact_rect = door["rect"].inflate(32, 32)
        if interact_rect.collidepoint(player.position.x, player.position.y):
            return door
        return None
    
    def open_door(self, door):
        """Open a door."""
        door["open"] = True


    def center(self, x, y):
        """Center the map on a world position."""
        self.map_layer.center((x, y))

    def draw(self, screen, camera_x, camera_y):
        """Draw the map and sprites."""
        self.group.center(pygame.math.Vector2(camera_x, camera_y))
        self.group.draw(screen)
