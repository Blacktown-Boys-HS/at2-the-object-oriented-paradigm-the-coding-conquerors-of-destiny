class Cave:
    def __init__(self, cave_name, num):
        self.name = cave_name
        self.description = None

    def get_description(self):
            return self.description
        
    def set_description(self, cave_description):
            self.description = cave_description