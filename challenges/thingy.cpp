#include <iostream>

int main() {
    std::cout << "
        This code defines the constructor method for the Cave class. When a Cave object is created, it automatically runs this method to set up the objects initial attributes.

        self.name = None creates an attribute for the cave object and sets its initial value to None, meaning the cave has no name until it's assigned one later.

        self.description = None does the same thing but for the description attribute, creating it and settings its initial value to None, meaning the cave has no description until one is provided.

        The self keyword refers to the specific object being created, so each Cave object gets it own seperate name and description attributes. Setting them to None is a way of declaring that these attributes exist but have not been given a value yet. They act as placeholders that can be filled in later using setter functions.

        This line of code is an important statement that allows the main.py file to access the Cave.py class that was defined in the seperate cave.py module.

        from cave tells Python to look inside the cave.py file, and import Cave specifically imports the Cave class from that module into the current programs namespace.

        This is necessary because Python does not automatically have access to code written in other files. By importing the Cave class, the main.py file can now instantiate Cave objects (Or in my case index.py as main.py is an already existing file for pygame) and call any of the methods and access any of the attributes defined within the Cave class, without needing to rewrite or duplicate any of that code. This promotes code modularity and reusability, which are key principles in object oriented programming.

        Nothing appears to have happened because this line of code only instantiates a Cave object and stores it in the variable cavern. It does not call methods that produce an output to the console.

        When the constructor __init__ is executed, it simply initialises the objects attributes in memory. There are no print statements or return values being displayed to the user at any point in the program.

        To see any output, a method such as describe() would need to be explicitly called on the object, which would then print data to the console. Without invoking a method that produces output, the program runs silently, meaning the object exists in memory but the user recieves no visual feedback that it has been created.

        Plans for a house are like a class because they serve as a blueprint that defines the structure and features of something without being the actual thing itself. The house plans describe attributes like the number of rooms, the dimensions, and the layout, but the plans themselves are not a physical house.

    "   
    return 0
}