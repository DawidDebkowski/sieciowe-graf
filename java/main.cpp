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

    computers[0] = {0, 7, 'A'};
    computers[1] = {1, 20, 'B'};
    computers[2] = {2, 50, 'C'};
    // computers[3] = {3, 19, 'D'};
    // computers[4] = {4, 20, 'E'};

    createMatrix();
    createPrintableComputers();
    initSavefile("./test.txt");
    printCable(0);
    saveCable();

    for (int second = 0; second < TIME; second++) {
        // this_thread::sleep_for(chrono::milliseconds(10));

        cablePropagation();
        computerBehaviour(second);
        printCable(second);
        saveCable();
    }

    saveFile.close();
    return 0;
}