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

        Getters and setters are methods defined in a class that are used to access and modify an object's attributes in a controlled way.

        A getter method retrieves the value of a private or encapsulated attribute and returns it to the caller. For example, get_description() returns the value stored in self.description. A setter method assigns or updates the value of an attribute by accepting a parameter and storing it inside the object. For example, set_description(cave_description) takes the provided value and assigns it to self.description.

        The first parameter of every method must always be self, which is a reference to the specific object that is invoking the method. This allows the method to access and modify the attributes and other methods of that particular object instance. When calling a method on an object, Python automatically passes self behind the scenes, so it does not need to be provided explicitly by the programmer.

        Nothing appears because get_description() is a getter method that uses the return keyword to send the value of self.description() back to the caller. However, simply returning a value does not automatically display it in the console.

        For output to be

    "   
    return 0
}