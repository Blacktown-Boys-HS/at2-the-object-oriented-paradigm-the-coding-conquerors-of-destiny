#include <iostream>

int main() {
    std::cout << "
        The method takes 3 parameters: self, cave_to_link, direction.

        However, in practice when the method is called on an object, only 2 arguements need to be provided by the programmer, as self is automatically passed in by Python as a reference to the object invoking the method. For example:
    
        This line of code invokes the link_cave method on the cavern object, passing in the dungeon object and the string "south" as arguments. Inside the method, this adds a new entry to the cavern object's linked_caves dictionary, where the key is "south" and the value is the dungeon object.

        The practical effect is that the dungeon is now stored as a linked cave in the south direction from the cavern. When the player types "south" during gameplay, the move method will look up "south" in the linked_caves dictionary, find the dungeon object, and return it as the new current_cave, effectively moving the player from the cavern into the dungeon.

        To fix this, an additional link_cave method call needs to be made on the dungeon object, creating a return path back to the cavern, this is done by adding the following line of code:

        This uses a for loop as its primary control structure to iterate over key stored in the linked_caves dictionary. In Python, iterating over a dictionary by default loops through its keys, so on each iteration the variable direction is assigned the next key in the dictionary, which in this case is a directional string such as "south" or "north".

        Inside the for loop, self.linked_caves[direction] uses the current direction key to look up and retrieve the corresponding cave object from the dictionary, storing it in the local variable cave. The getter method get_name() is then called on that object to retrieve its name attribute, and a print 

        "   
    return 0
}