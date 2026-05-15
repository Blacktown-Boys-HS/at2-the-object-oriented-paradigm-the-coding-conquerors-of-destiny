from uuid import NIL


class Character():
    def __init__(self, char_name, char_description):
        self.name = char_name
        self.description = char_description
        self.conversation = None

    def describe(self):
        print(self.name + " is here!")
        print(self.description)

    def set_conversation(self, conversation):
        self.conversation = conversation

    def talk(self):
        if self.conversation != NIL:
            print("[" + self.name + " says]: " + self.conversation)
        else:
            print(self.name + " doesn't want to talk to you")
    
    def fight(self, combat_item):
        print(self.name + " doesn't want to fight with you")
        return True
