# Dungeon's End

Dungeon's End is a top-down dungeon RPG built with Python and Pygame. The project uses an object-oriented structure with separate classes for the application loop, scene management, player behaviour, enemies, projectiles, pickups, UI panels, audio, and Tiled map loading.

## Features

- Main menu, tutorial, settings, credits, pause menu, game over screen, and victory screen
- Tiled map support with collision objects, triggers, doors, keys, hazards, enemy spawns, and potion spawns
- Animated player sprite with movement, health, melee attack, fireball attack, damage cooldowns, and regeneration
- Slime enemies, a purple slime boss, boss projectiles, health potions, inventory hotbar, and task panel
- Scene transitions, custom cursor, sound effects, and background music

## Requirements

- Python 3.10+
- pygame
- pytmx
- pyscroll
- numpy

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Running

```bash
python3 main.py
```

## Controls

| Input | Action |
| --- | --- |
| `WASD` / Arrow keys | Move |
| `E` | Interact |
| `F` | Slash attack |
| Right mouse / `R` | Fireball |
| Number keys / Mouse wheel | Select hotbar slot |
| `Esc` | Pause |
| `F3` | Debug menu |

## Project Structure

```text
main.py              Entry point
game_app.py          Pygame setup and main loop
scene_manager.py     Scene creation and scene switching
scenes/              Menu, game, tutorial, settings, HUD, and UI screens
player.py            Player state, movement, health, animation, and attacks
enemy.py             Slime enemy and boss enemy classes
projectiles.py       Player and boss projectile classes
pickups.py           Collectible pickup classes
scenes/world.py      Tiled map loading, collision, triggers, and map objects
sounds.py            Sound effects and background music
assets/              Maps, sprites, fonts, music, and sound effects
```

## Team

Coding Conquerors of Destiny

- Angadjot Dhaliwal
- Shivesh Sundar
- Sri Hari Srinigganathan

## Built With

- Pygame
- pytmx
- pyscroll
- Tiled
