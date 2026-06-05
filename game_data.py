"""
Objectives, controls, and tutorial copy — single source for in-game tasks and the menu tutorial.
"""

OBJECTIVES = [
    {
        "id": "find_key",
        "text": "Find a key",
        "detail": "Explore the dungeon. When you stand near a key, press E to collect it.",
    },
    {
        "id": "unlock_door",
        "text": "Unlock a door",
        "detail": "Use keys from your inventory on locked doors and doorways (press E).",
    },
    {
        "id": "escape",
        "text": "Escape the dungeon",
        "detail": "Survive hazards, manage your health, and find a way out of the depths.",
    },
]

CONTROLS = [
    ("Move", "WASD or Arrow Keys"),
    ("Interact", "E — pick up keys, open doors, unlock gates"),
    ("Pause", "ESC — pause menu (resume, settings, or quit to menu)"),
    ("Hotbar", "1–9 or mouse wheel — select inventory slots"),
    ("Tasks panel", "Click the gold tab — show or hide your objectives"),
]

SURVIVAL_TIPS = [
    "Read the opening dialogue when you enter the dungeon.",
    "Check the Tasks panel (top-right) for your current objectives.",
    "Hazards on the floor drain health — step around them.",
    "If health reaches zero, you get Game Over and can retry.",
    "Volume sliders live in Settings on the main menu.",
]


def objective_task_list():
    """Task panel rows derived from OBJECTIVES."""
    return [{"text": obj["text"], "done": False} for obj in OBJECTIVES]


def tutorial_sections():
    """Sections shown on the Tutorial menu screen."""
    objective_lines = [
        f"{obj['text']} — {obj['detail']}" for obj in OBJECTIVES
    ]
    control_lines = [f"{name}: {desc}" for name, desc in CONTROLS]
    return [
        {"title": "Controls", "lines": control_lines},
        {"title": "Objectives", "lines": objective_lines},
        {"title": "Survival", "lines": SURVIVAL_TIPS},
    ]
