from cave import Cave

cavern = Cave("cavern")
cavern.set_description("A damp and dity cave.")

dungeon = Cave("Dungeon")
dungeon.set_description("A large cave with a rack")

grotto = Cave("grotto")
grotto.set_description("A small cave with ancient graffiti.")

# Linking
cavern.link_cave(dungeon, "south")
grotto.link_cave(dungeon, "east")
dungeon.link_cave(grotto, "west")

cavern.get_details()