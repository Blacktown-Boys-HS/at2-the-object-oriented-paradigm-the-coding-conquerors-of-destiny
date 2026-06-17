"""
World module for the RPG game.
"""

import pygame
import pyscroll
import pytmx

from globals import SCREEN_HEIGHT, SCREEN_WIDTH


class World:
    """Loads and manages the game map, collision rects, hazard rects, doors, keys, locked doors and above zones."""

    # INITIALIZATION

    def __init__(self, tmx_path, player, zoom=3.0, default_layer=8):
        self.map_layer = None
        self.map_width = 0
        self.map_height = 0
        self.collision_rects = []
        self.hazard_rects = []
        self.doors = []
        self.keys = []
        self.locked_doors = []
        self.above_zones = []
        self.group = None
        self.zoom = zoom
        self.enemy_spawns = []

        tmx_data = pytmx.load_pygame(str(tmx_path), pixelalpha=True)

        map_data = pyscroll.data.TiledMapData(tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(
            map_data, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.map_layer.zoom = zoom
        self.map_width = tmx_data.width * tmx_data.tilewidth
        self.map_height = tmx_data.height * tmx_data.tileheight

        # Load all objects from tiled map
        self._load_objects_from_tiled(tmx_data)

        # pyscroll group for z-ordering
        self.group = pyscroll.PyscrollGroup(
            map_layer=self.map_layer, default_layer=default_layer
        )
        self.group.add(player)

    # INITIALIZATION (continued)

    def _load_objects_from_tiled(self, tmx_data):
        """Extract and parse all objects from tiled map data.

        Categorizes objects into collision rects, hazards, doors, keys, locked doors,
        and above zones based on object names and properties.
        """
        for obj in tmx_data.objects:
            if obj.x is not None:
                try:
                    rect = pygame.Rect(
                        int(obj.x), int(obj.y), int(obj.width), int(obj.height)
                    )
                    name = (obj.name or "").lower()
                    if name == "hazard":
                        self.hazard_rects.append(rect)
                    elif name == "door":
                        self.doors.append(
                            {
                                "rect": rect,
                                "open": False,
                                "id": obj.properties.get("door_id", 0),
                                "required_key_id": obj.properties.get(
                                    "required_key_id", None
                                ),
                            }
                        )
                    elif name == "locked_door":
                        self.locked_doors.append(
                            {
                                "rect": rect,
                                "locked": True,
                                "id": obj.properties.get("door_id", 0),
                                "required_key_id": obj.properties.get(
                                    "required_key_id", None
                                ),
                            }
                        )
                    elif name == "key":
                        self.keys.append(
                            {
                                "rect": rect,
                                "collected": False,
                                "id": obj.properties.get("key_id", "key"),
                            }
                        )
                    elif name == "above":
                        self.above_zones.append(rect)
                    elif name == "enemy_spawn":
                        self.enemy_spawns.append((int(obj.x), int(obj.y)))
                    else:
                        self.collision_rects.append(rect)
                except Exception:
                    pass

    # COLLISION DETECTION

    def get_collision_rects(self):
        """Return collision rects plus any closed doors and locked doors."""
        closed_doors = [d["rect"] for d in self.doors if not d["open"]]
        locked_door_rects = [d["rect"] for d in self.locked_doors if d["locked"]]
        return self.collision_rects + closed_doors + locked_door_rects

    def check_collision_x(self, player_rect, old_x, player):
        """Check horizontal collision only."""
        for rect in self.get_collision_rects():
            if player_rect.colliderect(rect):
                player.position.x = old_x
                break

    def check_collision_y(self, player_rect, old_y, player):
        """Check vertical collision only."""
        for rect in self.get_collision_rects():
            if player_rect.colliderect(rect):
                player.position.y = old_y
                break

    # HAZARD DETECTION

    def check_hazard(self, player_rect, player):
        """Check hazard collision and apply damage. Returns True if hit."""
        for rect in self.hazard_rects:
            if player_rect.colliderect(rect):
                player.take_damage(10)
                return True
        return False

    # PROXIMITY DETECTION (Doors, Keys, Locked Doors)

    def get_nearby_door(self, player):
        """Return the nearest closed door if player is close enough."""
        for door in self.doors:
            if door["open"]:
                continue
            if (
                door["rect"]
                .inflate(32, 32)
                .collidepoint(player.position.x, player.position.y)
            ):
                return door
        return None

    def get_nearby_locked_door(self, player):
        """Return the nearest locked door if player is close enough."""
        for door in self.locked_doors:
            if not door["locked"]:
                continue
            if (
                door["rect"]
                .inflate(32, 32)
                .collidepoint(player.position.x, player.position.y)
            ):
                return door
        return None

    def get_nearby_key(self, player):
        """Return the nearest uncollected key if player is close enough."""
        for key in self.keys:
            if key["collected"]:
                continue
            if (
                key["rect"]
                .inflate(32, 32)
                .collidepoint(player.position.x, player.position.y)
            ):
                return key
        return None

    # DOOR MANAGEMENT

    def open_door(self, door):
        """Open a door."""
        door["open"] = True

    def unlock_door(self, door):
        """Unlock a locked door."""
        door["locked"] = False

    def reset_doors(self):
        """Reset all doors to closed."""
        for door in self.doors:
            door["open"] = False

    def reset_locked_doors(self):
        """Reset all locked doors to locked."""
        for door in self.locked_doors:
            door["locked"] = True

    # KEY MANAGEMENT

    def collect_key(self, key):
        """Mark a key as collected."""
        key["collected"] = True

    def reset_keys(self):
        """Reset all keys to uncollected."""
        for key in self.keys:
            key["collected"] = False

    # RENDERING & CAMERA

    def update_player_layer(self, player):
        """Swap player z-layer based on above zone position."""
        player_rect = pygame.Rect(player.position.x - 4, player.position.y - 4, 8, 8)
        in_above_zone = any(player_rect.colliderect(z) for z in self.above_zones)
        target_layer = 100 if in_above_zone else 8
        if self.group.get_layer_of_sprite(player) != target_layer:
            self.group.change_layer(player, target_layer)

    def center(self, x, y):
        """Center the map on a world position."""
        self.map_layer.center((x, y))

    def draw(self, screen, camera_x, camera_y):
        """Draw the map and sprites."""
        self.group.center(pygame.math.Vector2(camera_x, camera_y))
        self.group.draw(screen)
