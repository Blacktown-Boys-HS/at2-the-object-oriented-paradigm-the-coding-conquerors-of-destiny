#include <iostream>

int main() {
    std::cout << "
        The method takes 3 parameters: self, cave_to_link, direction.

        However, in practice when the method is called on an object, only 2 arguements need to be provided by the programmer, as self is automatically passed in by Python as a reference to the object invoking the method. For example:
    
        This line of code invokes the link_cave method on the cavern object, passing in the dungeon object and the string "south" as arguments. Inside the method, this adds a new entry to the cavern object's linked_caves dictionary, where the key is "south" and the value is the dungeon object.

        The practical effect is that the dungeon is now stored as a linked cave in the south direction from the cavern. When the player types "south" during gameplay, the move method will look up "south" in the linked_caves dictionary, find the dungeon object, and return it as the new current_cave, effectively moving the player from the cavern into the dungeon.

        To fix this, an additional link_cave method call needs to be made on the dungeon object, creating a return path back to the cavern, this is done by adding the following line of code:

        This uses a for loop as its primary control structure to iterate over key stored in the linked_caves dictionary. In Python, iterating over a dictionary by default loops through its keys, so on each iteration the variable direction is assigned the next key in the dictionary, which in this case is a directional string such as "south" or "north".

        Inside the for loop, self.linked_caves[direction] uses the current direction key to look up and retrieve the corresponding cave object from the dictionary, storing it in the local variable cave. The getter method get_name() is then called on that object to retrieve its name attribute, and a print statement concatenates the name and direction together to produce a formatted output line such as "The dungeon is south".

        This process repeats for every key-value pair in the linked_caves dictionary, meaning every cave linked to the current cave gets printed to the console. This is an example of how iteration over a data structure combined with method calls on stored objects allow complex information to be retrieved and display efficiently in an OOP program.

        A move method would take a direction as a parameter, which is the command inputted by the player during gameplay. It would then check whether that direction exists as a key inside the current cave object's linked_caves dictionary using an if statement.

        If the direction is found in the dictionary, the method retrieves the cave object stored at that key and returns it. This returned cave objet then becomes the new current_cave in the main game loop, effectively moving the player into that cave and triggering its details to be displayed to the console.

        If the direction is not found in the dictionary, the else branch executes, printing a message to inform the player that they cannot travel in that direction. The method then returns self, which is a reference to the current cave object, meaning the players stays in the same cave and the game loop continues from their current position without any changes in location.

        To create a Character object, two arguments must be provided at the point of instantiation: char_name and char_description. These are the required parameters defined in the constructor, meaning Python will raise an error if either is missing when the object is created.

        Here "Harry" is passed as char_name and "A smelly Wumpus" is passed as char_description. When the constructor executes, these values are assigned to self.name and self.description respectively, storing them as attributes on the object instance.

        The third attribute self.conversation is automatically initialised to None inside the constructor without requiring any input from the programmer. This means the character has no dialogue by default, but the set_conversation() setter method can be called later to assign one. This is an example of encapsulation, where the object is initialised in a controlled, predictable state and attributes are modified through defined methods rather than being set arbitrarly from outside the class.

        "   
    return 0
}