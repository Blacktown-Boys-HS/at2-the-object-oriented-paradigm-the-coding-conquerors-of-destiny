class Cave:
    def __init__(self, cave_name):
        self.name = cave_name
        self.description = None
        self.linked_caves = {}

    def get_description(self):
            return self.description
        
    def set_description(self, cave_description):
            self.description = cave_description

    def set_name(self, cave_name):
          self.name = cave_name

    def get_name(self):
          return self.name

    def set_character(self, new_character):
          self.character = new_character

    def get_character(self):
          return self.character

    def describe(self):
          print(self.description)

    def link_cave(self, cave_to_link, direction):
          self.linked_caves[direction] = cave_to_link

    def get_details(self):
          print(self.name)
          print("-------------")
          print(self.description)
          for direction in self.linked_caves:
                cave = self.linked_caves[direction]
                print("The " + cave.get_name() + " is " + direction)    