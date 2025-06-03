// #include <iostream>
// #include <string>
// #include <chrono>
// #include <thread>

#include "const.cpp"
#include "computer.cpp"
#include "cable.cpp"

using namespace std;

int main() {
    initCable();
    computers[0] = {0, 1, 'A'};
    computers[1] = {1, 39, 'B'};
    computers[2] = {2, 28, 'C'};
    computers[3] = {3, 19, 'X'};
    computers[4] = {4, 20, 'D'};
    createMatrix();
    createPrintableComputers();
    initSavefile("./test.txt");
    printCable(0);
    saveCable();

    // cable[2].left_propagation = true;
    // cable[2].symbol = 'A';
    // cable[2].changed = true;
    // cable[2].right_propagation = true;

    // cable[19].symbol = 'B';
    // cable[19].left_propagation = true;
    // cable[19].changed = true;
    // cable[19].right_propagation = true;

    for (int second = 0; second < TIME; second++) {
        this_thread::sleep_for(chrono::milliseconds(10));

        cablePropagation();
        computerBehaviour(second);
        printCable(second);
        saveCable();
    }

    saveFile.close();
    return 0;
}