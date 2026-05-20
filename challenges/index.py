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

    if command == "talk":
        if inhabitant is not None:
            inhabitant.talk()
    elif command == "fight":
        if inhabitant is not None and isinstance(inhabitant, Enemy):
            print("What will you fight with?")
            fight_with = input()
            if inhabitant.fight(fight_with) == True:
                print("Bravo, hero you won the fight!")
                dungeon.set_character(None)
                if Enemy.enemies_to_defeat == 0:
                    print("Congratulations, you have survived another adventure!")
                    dead = True
            else:
                print("Scurry home, you lost the fight.")
                print("That's the end of the game")
                dead = True
        else:
            print("There is no one here to fight with")
    else:
        current_cave = current_cave.move(command)