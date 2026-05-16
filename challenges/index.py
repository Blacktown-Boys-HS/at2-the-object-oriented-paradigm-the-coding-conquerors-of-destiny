from cave import Cave
from character import Enemy

cavern = Cave("Cavern")
cavern.set_description("A dank and dirty cave")

dungeon = Cave("Dungeon")
dungeon.set_description("A large cave with a rack")

grotto = Cave("Grotto")
grotto.set_description("A small cave with ancient graffiti")

dungeon.link_cave(cavern, "north")
dungeon.link_cave(grotto, "east")
cavern.link_cave(dungeon, "south")
grotto.link_cave(dungeon, "west")

harry = Enemy("Harry", "A smelly Wumpus")
harry.set_conversation("Hangry...Hanggrry")
harry.set_weakness("vegemite")

dungeon.set_character(harry)

dead = False
current_cave = cavern

while dead == False:
    print("\n")
    current_cave.get_details()

    inhabitant = current_cave.get_character()
    if inhabitant is not None:
        inhabitant.describe()

    command = input("> ")
    current_cave = current_cave.move(command)