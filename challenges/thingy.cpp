#include <iostream>

void challenge_24(std::string);

int main() {
    challenge_24("yes");
    return 0;
}

void challenge_24(std::string txt) {
    if (txt == "yes") {
        std::cout << "
           e
        "
    } else std::cout << "go away flop";
}
