"""
Enemy classes for the RPG game.
"""
import math
import random
import pygame
from pathlib import Path
from sprite_sheet import SpriteSheet
from pos import Position


class SlimeEnemy(pygame.sprite.Sprite):
    """Green slime enemy with roam and chase AI."""

    FRAME_WIDTH = 24
    FRAME_HEIGHT = 24
    DISPLAY_SCALE = 1

    # AI states
    STATE_ROAM = "roam"
    STATE_CHASE = "chase"
    STATE_HIT = "hit"
    STATE_DEAD = "dead"

    ROAM_SPEED = 25
    CHASE_SPEED = 45     
    DETECT_RADIUS = 80    
    LOSE_RADIUS = 75
    ROAM_CHANGE_TIME = 2.0  

    MAX_HEALTH = 30
    CONTACT_DAMAGE = 10
    CONTACT_COOLDOWN = 0.8  

    def __init__(self, x, y):
        super().__init__()
        self.position = Position(float(x), float(y))
        self.ai_state = self.STATE_ROAM
        self.facing_right = True

        self.health = self.MAX_HEALTH
        self.damage_cooldown = 0.0
        self.contact_cooldown = 0.0
        self.hit_timer = 0.0
        self.hit_duration = 0.4

        # Roam state
        self.roam_dx = random.choice([-1, 0, 1])
        self.roam_dy = random.choice([-1, 0, 1])
        self.roam_timer = random.uniform(0.5, self.ROAM_CHANGE_TIME)

        # Animation
        self.animation_time = 0.0
        self.current_frame = 0
        self.sprite_sheet = None

        slime_path = (
            Path(__file__).resolve().parent
            / "assets" / "rpg_assets" / "sprites" / "slime_green.png"
        )
        try:
            self.sprite_sheet = SpriteSheet(slime_path, self.FRAME_WIDTH, self.FRAME_HEIGHT)
            self.animations = {
                "walk": {"frames": self.sprite_sheet.get_animation(0, 0, 4), "speed": 6},
                "hit":  {"frames": self.sprite_sheet.get_animation(2, 0, 4), "speed": 8},
            }
        except (FileNotFoundError, pygame.error) as e:
            print(f"Warning: Could not load slime sprite: {e}")
            self.sprite_sheet = None

        # pyscroll needs these
        self.image = pygame.Surface((self.FRAME_WIDTH, self.FRAME_HEIGHT), pygame.SRCALPHA)
        self.rect = pygame.Rect(x, y, self.FRAME_WIDTH, self.FRAME_HEIGHT)

    @property
    def is_dead(self):
        return self.health <= 0

    def take_damage(self, amount):
        if self.damage_cooldown <= 0 and self.ai_state != self.STATE_DEAD:
            self.health = max(0, self.health - amount)
            self.damage_cooldown = 0.5
            if self.is_dead:
                self.ai_state = self.STATE_DEAD
            else:
                self.ai_state = self.STATE_HIT
                self.hit_timer = self.hit_duration

    def update(self, dt, player_pos=None, collision_rects=None):
        """Update AI, movement, and animation."""
        if self.ai_state == self.STATE_DEAD:
            self._update_animation(dt)
            self.rect.center = (int(self.position.x), int(self.position.y))
            return

        # Tick cooldowns
        self.damage_cooldown = max(0.0, self.damage_cooldown - dt)
        self.contact_cooldown = max(0.0, self.contact_cooldown - dt)

        # Hit state timer
        if self.ai_state == self.STATE_HIT:
            self.hit_timer -= dt
            if self.hit_timer <= 0:
                self.ai_state = self.STATE_ROAM

        # AI state transitions
        if player_pos and self.ai_state not in (self.STATE_HIT,):
            dist = math.sqrt(
                (self.position.x - player_pos.x) ** 2 +
                (self.position.y - player_pos.y) ** 2
            )
            if dist < self.DETECT_RADIUS:
                self.ai_state = self.STATE_CHASE
            elif dist > self.LOSE_RADIUS and self.ai_state == self.STATE_CHASE:
                self.ai_state = self.STATE_ROAM

        # Movement
        dx, dy = 0.0, 0.0
        if self.ai_state == self.STATE_CHASE and player_pos:
            dx = player_pos.x - self.position.x
            dy = player_pos.y - self.position.y
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length
            speed = self.CHASE_SPEED
        elif self.ai_state == self.STATE_ROAM:
            self.roam_timer -= dt
            if self.roam_timer <= 0:
                self.roam_dx = random.choice([-1, 0, 0, 1])
                self.roam_dy = random.choice([-1, 0, 0, 1])
                self.roam_timer = random.uniform(0.8, self.ROAM_CHANGE_TIME)
            dx, dy = float(self.roam_dx), float(self.roam_dy)
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length
            speed = self.ROAM_SPEED
        else:
            speed = 0

        if speed > 0 and (dx != 0 or dy != 0):
            old_x = self.position.x
            old_y = self.position.y

            # Move X
            self.position.x += dx * speed * dt
            if collision_rects:
                hit_rect = pygame.Rect(self.position.x - 4, self.position.y + 4, 8, 4)
                for rect in collision_rects:
                    if hit_rect.colliderect(rect):
                        self.position.x = old_x
                        self.roam_dx *= -1
                        break

            # Move Y
            self.position.y += dy * speed * dt
            if collision_rects:
                hit_rect = pygame.Rect(self.position.x - 4, self.position.y + 4, 8, 4)
                for rect in collision_rects:
                    if hit_rect.colliderect(rect):
                        self.position.y = old_y
                        self.roam_dy *= -1
                        break

            if dx > 0:
                self.facing_right = True
            elif dx < 0:
                self.facing_right = False

        self._update_animation(dt)
        self.rect.center = (int(self.position.x), int(self.position.y))

    def _update_animation(self, dt):
        if not self.sprite_sheet:
            return

        anim_key = "hit" if self.ai_state in (self.STATE_HIT, self.STATE_DEAD) else "walk"
        anim = self.animations[anim_key]
        self.animation_time += dt
        frame_index = int(self.animation_time * anim["speed"])
        self.current_frame = frame_index % len(anim["frames"])

        sprite = anim["frames"][self.current_frame]
        scaled = pygame.transform.scale(sprite, (
            int(sprite.get_width() * self.DISPLAY_SCALE),
            int(sprite.get_height() * self.DISPLAY_SCALE)
        ))
        if not self.facing_right:
            scaled = pygame.transform.flip(scaled, True, False)
        self.image = scaled
        self.rect = self.image.get_rect(center=self.rect.center)

    def check_contact_damage(self, player):
        """Deal contact damage to player if overlapping. Call each frame."""
        if self.ai_state == self.STATE_DEAD:
            return
        if self.contact_cooldown > 0:
            return
        slime_rect = pygame.Rect(self.position.x - 8, self.position.y - 8, 16, 16)
        player_rect = pygame.Rect(self.position.x - 4, self.position.y + 8, 8, 4)
        player_check = pygame.Rect(player.position.x - 4, player.position.y + 8, 8, 4)
        if slime_rect.colliderect(player_check):
            if player.damage_cooldown <= 0:
                player.take_damage(self.CONTACT_DAMAGE)
                self.contact_cooldown = self.CONTACT_COOLDOWN