#include <iostream>
#include <string>
#include <chrono>
#include <thread>

#include "const.cpp"
#include "computer.cpp"
#include "cable.cpp"

using namespace std;

int main() {
    initCable();
    computers[1] = {0, 1, 'A'};
    computers[19] = {1, 19, 'B'};
    printCable();

    cable[2].left_propagatoin = true;
    cable[2].symbol = 'A';
    cable[2].changed = true;
    cable[2].right_propagatoin = true;

    cable[19].symbol = 'B';
    cable[19].left_propagatoin = true;
    cable[19].changed = true;
    cable[19].right_propagatoin = true;

    for (int second = 0; second < TIME; second++) {
        this_thread::sleep_for(chrono::milliseconds(500));

        cablePropagation();
        computerBehaviour(second);
        printCable();
    }

    return 0;
}