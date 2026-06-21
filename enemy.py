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
    SPRITE_NAME = "slime_green.png"

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

    MAX_HEALTH = 75
    CONTACT_DAMAGE = 10
    CONTACT_COOLDOWN = 1.2

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
            / "assets" / "rpg_assets" / "sprites" / self.SPRITE_NAME
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
                hit_rect = self.get_hit_rect()
                for rect in collision_rects:
                    if hit_rect.colliderect(rect):
                        self.position.x = old_x
                        self.roam_dx *= -1
                        break

            # Move Y
            self.position.y += dy * speed * dt
            if collision_rects:
                hit_rect = self.get_hit_rect()
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

    def get_hit_rect(self):
        """Return the enemy collision / attack hitbox."""
        width = int(16 * self.DISPLAY_SCALE)
        height = int(12 * self.DISPLAY_SCALE)
        return pygame.Rect(
            int(self.position.x - width / 2),
            int(self.position.y - height / 2),
            width,
            height,
        )

    def check_contact_damage(self, player):
        """Deal contact damage to player if overlapping. Call each frame."""
        if self.ai_state == self.STATE_DEAD:
            return
        if self.contact_cooldown > 0:
            return
        slime_rect = self.get_hit_rect()
        player_check = pygame.Rect(player.position.x - 4, player.position.y + 8, 8, 4)
        if slime_rect.colliderect(player_check):
            if player.damage_cooldown <= 0:
                player.take_damage(self.CONTACT_DAMAGE)
                self.contact_cooldown = self.CONTACT_COOLDOWN

    def render_health_bar(self, screen, camera, zoom):
        """Render a health bar above the slime."""
        from globals import SCREEN_WIDTH, SCREEN_HEIGHT
        if self.ai_state == self.STATE_DEAD:
            return

        screen_x = (self.position.x - camera.x) * zoom + SCREEN_WIDTH / 2
        screen_y = (self.position.y - camera.y) * zoom + SCREEN_HEIGHT / 2

        bar_width = 24
        bar_height = 4
        bar_x = int(screen_x - bar_width / 2)
        bar_y = int(screen_y - 28)

        # Shadow
        pygame.draw.rect(screen, (0, 0, 0), (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2), border_radius=2)
        # Background
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height), border_radius=2)
        # Fill
        health_pct = self.health / self.MAX_HEALTH
        fill_width = max(0, int(bar_width * health_pct))
        if fill_width > 0:
            pygame.draw.rect(screen, (0, 180, 0), (bar_x, bar_y, fill_width, bar_height), border_radius=2)
        # Border
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1, border_radius=2)


class BossSlimeEnemy(SlimeEnemy):
    """Large purple slime boss."""

    NAME = "The Violet Slime King"
    DISPLAY_SCALE = 3
    SPRITE_NAME = "slime_purple.png"

    MAX_HEALTH = 500
    CONTACT_DAMAGE = 25
    CONTACT_COOLDOWN = 1.0

    def update(self, dt, player_pos=None, collision_rects=None):
        """Update animation only; the boss stays still and attacks with projectiles."""
        if self.ai_state == self.STATE_DEAD:
            self._update_animation(dt)
            self.rect.center = (int(self.position.x), int(self.position.y))
            return

        self.damage_cooldown = max(0.0, self.damage_cooldown - dt)
        self.contact_cooldown = max(0.0, self.contact_cooldown - dt)

        if self.ai_state == self.STATE_HIT:
            self.hit_timer -= dt
            if self.hit_timer <= 0:
                self.ai_state = self.STATE_ROAM

        if player_pos:
            if player_pos.x > self.position.x:
                self.facing_right = True
            elif player_pos.x < self.position.x:
                self.facing_right = False

        self._update_animation(dt)
        self.rect.center = (int(self.position.x), int(self.position.y))


class BossProjectile:
    """Projectile fired by the boss in the arena."""

    def __init__(self, x, y, vx, vy, radius=5, damage=12, lifetime=4.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.radius = radius
        self.damage = damage
        self.lifetime = lifetime
        self.age = 0.0
        self.active = True

    def update(self, dt):
        """Move the projectile and expire it after its lifetime."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False

    def get_rect(self):
        """Return collision rect for hitting the player."""
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def render(self, screen, camera, zoom, time_seconds=0.0):
        """Draw projectile directly on the screen."""
        from globals import SCREEN_WIDTH, SCREEN_HEIGHT

        screen_x = int((self.x - camera.x) * zoom + SCREEN_WIDTH / 2)
        screen_y = int((self.y - camera.y) * zoom + SCREEN_HEIGHT / 2)
        draw_radius = max(3, int(self.radius * zoom))

        pulse = 0.5 + 0.5 * math.sin(time_seconds * 10 + self.age * 8)
        core = (
            min(255, int(180 + 45 * pulse)),
            min(255, int(80 + 30 * pulse)),
            255,
        )
        rim = (70, 20, 100)

        pygame.draw.circle(screen, rim, (screen_x, screen_y), draw_radius + 2)
        pygame.draw.circle(screen, core, (screen_x, screen_y), draw_radius)
        pygame.draw.circle(
            screen,
            (245, 210, 255),
            (screen_x - draw_radius // 3, screen_y - draw_radius // 3),
            max(1, draw_radius // 3),
        )
