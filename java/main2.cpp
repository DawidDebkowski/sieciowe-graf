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
    computers[1] = {0, 'A'};
    computers[19] = {1, 'B'};
    printCable();

    cable[1].symbol = 'A';
    for (int second = 0; second < TIME; second++) {
        this_thread::sleep_for(chrono::seconds(1));

        cablePropagation();
        computerBehaviour();
        printCable();
    }

    return 0;
}