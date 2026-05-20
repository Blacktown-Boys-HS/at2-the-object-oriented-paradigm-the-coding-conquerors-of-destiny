#include <iostream>

void challenge_24(std::string);

int main() {
    challenge_24("yes");
    return 0;
}

void challenge_24(std::string txt) {
    if (txt == "yes") {
        std::cout << "
            The cave can contain a character even though Harry is an Enemy because of inheritance. The character attribute inside the Cave class is designed to store any object that is an instance of the Character class. Since Enemy is a subclass of Character, any Enemy object is also considered to be a Character object by Python.

            This means that when dungeon.set_character(henry) is called, Python accepts the Enemy object as a valid value for the character attribute because Enemy inherits from Character, making Harry both an Enemy instance and a Character instance at the same time. This can be verified using the isinstance() function.

            This is a key principle of inheritance in OOP, where a subclass object can be used anywhere its superclass is expected. The Cave class does not need to know whether the stored object is specifically a Character or an Enemy, it simply stores whatever object is passed in. The distinction between the two is only made later in the game loop using isinstance() to check whether the inhabitant is an Enemy before allowing the player to initiate a fight.

        ";
    } else std::cout << "go away flop";
}
