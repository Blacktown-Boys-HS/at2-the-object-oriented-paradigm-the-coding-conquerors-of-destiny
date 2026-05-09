[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/tZXTeiOZ)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23769192&assignment_repo_type=AssignmentRepo)

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/tZXTeiOZ)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23769192&assignment_repo_type=AssignmentRepo)

---

```
██████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗    ███████╗
██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║    ██╔════╝
██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║    ███████╗
██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║    ╚════██║
██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║    ███████║
╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚══════╝
```

# ⚔️ Dungeon's End

> *You wake up in a dungeon. You don't know how you got here. You don't know what lurks in the dark. All you know is — you need to get out.*

A top-down dungeon RPG built in Python with Pygame. Fight through procedurally-designed dungeons, avoid traps, and uncover the mystery of how you ended up here.

---

## 🎮 Gameplay

- Explore hand-crafted dungeon maps built in Tiled
- Smooth knight animations — idle, run, roll, attack, and death
- Atmospheric lighting and layered tile rendering
- Dialogue system with typewriter effect
- Pause menu with scene transitions

---

## 🕹️ Controls

| Key | Action |
|-----|--------|
| `W` / `↑` | Move Up |
| `S` / `↓` | Move Down |
| `A` / `←` | Move Left |
| `D` / `→` | Move Right |
| `ESC` | Pause / Unpause |
| `Enter` / `Space` | Confirm |
| `Click` | Navigate Menus |

---

## 🚀 Installation

**Requirements:** Python 3.10+

```bash
# Clone the repo
git clone <your-repo-url>
cd <your-repo-folder>

# Install dependencies
pip install pygame pytmx pyscroll

# Run the game
python main.py
```

---

## 🗂️ Project Structure

```
📦 project root
 ┣ 📂 assets/
 ┃ ┣ 📂 maps/          # Tiled .tmx dungeon maps
 ┃ ┣ 📂 fonts/         # Pixel fonts
 ┃ ┣ 📂 rpg_assets/    # Sprites and tilesets
 ┃ ┗ 📂 cursor/        # Custom cursor
 ┣ 📂 scenes/
 ┃ ┣ game.py           # Main game scene
 ┃ ┣ menu.py           # Main menu
 ┃ ┣ credits.py        # Credits screen
 ┃ ┗ settings.py       # Settings screen
 ┣ camera.py           # Smooth camera with lerp
 ┣ player.py           # Player class + animations
 ┣ main.py             # Entry point + scene manager
 ┗ globals.py          # Constants and config
```

---

## 👾 Team

**Coding Conquerors of Destiny™**

| Name | Role |
|------|------|
| Angadjot Dhaliwal | Developer |
| Shivesh Sundar | Developer |
| Sri Hari Srinigganathan | Developer |

---

## 📚 Built With

- [Pygame](https://www.pygame.org/) — game framework
- [pytmx](https://github.com/bitcraft/pytmx) — Tiled map loader
- [pyscroll](https://github.com/bitcraft/pyscroll) — scrolling map renderer
- [Tiled](https://www.mapeditor.org/) — map editor

---

*Coding Conquerors of Destiny™ — HSC Software Engineering, 2025*