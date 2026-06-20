"""
Main entry point for the RPG game.
"""

import asyncio

from game_app import GameApp


async def main():
    """Create and run the game app."""
    app = GameApp()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
