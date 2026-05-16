from numpy import character
from cave import Cave
from character import Character

cavern = Cave("Cavern")
cavern.set_description("A damp and dity cave.")

dungeon = Cave("Dungeon")
dungeon.set_description("A large cave with a rack")

grotto = Cave("Grotto")
grotto.set_description("A small cave with ancient graffiti.")

# Linking
dungeon.link_cave(grotto, "east")
dungeon.link_cave(cavern, "north")
cavern.link_cave(dungeon, "south")
grotto.link_cave(dungeon, "west")

current_cave = cavern

while True:
    print("\n")
    current_cave.get_details()
    command = input("> ")
    current_cave = current_cave.move(command)
