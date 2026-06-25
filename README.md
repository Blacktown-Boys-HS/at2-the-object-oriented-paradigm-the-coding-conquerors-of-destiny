[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/tZXTeiOZ)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23769192&assignment_repo_type=AssignmentRepo)

# Dungeon's End

Dungeon's End is a top-down dungeon RPG built with Python and Pygame. The project uses an object-oriented structure with separate classes for the application loop, scene management, player behaviour, enemies, projectiles, pickups, UI panels, audio, and Tiled map loading.

## Game Play

### Start

https://github.com/user-attachments/assets/c447b470-c3f5-4db6-aaf5-161655aa0621

### Boss fight

https://github.com/user-attachments/assets/c74a9114-5c6d-4575-b98f-ad10d715a07a

### Victory

https://github.com/user-attachments/assets/6edb33ed-2171-4aa0-9d1f-c55f7aeef5df

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
