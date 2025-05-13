#include <iostream>
#include <string>
#include <chrono>
#include <thread>

using namespace std;

const int CABLE_SIZE = 20;
const int PC_NUMBER = 3;

const char EMPTY_SYMBOL = '-';

struct cablePart {
    bool changed;
    char symbol;
};

cablePart cable[CABLE_SIZE];
char computers[CABLE_SIZE];

const int TIME = 30;

void initCable() {
    for(int i=0;i<CABLE_SIZE;i++) {
        cable[i] = {false, EMPTY_SYMBOL};
        computers[i] = ' ';
    }
}

void printCable() {
    cout << "\033[2J\033[1;1H";
    cout << "|";
    for(int i=0;i<CABLE_SIZE;i++) {
        cout << cable[i].symbol;
    }
    cout << "|";
    cout << endl << ' ';
    for(int i=0;i<CABLE_SIZE;i++) {
        if(computers[i] != ' ') {
            cout << '|';
        } else cout << ' ';
    }
    cout << endl << ' ';
    for(int i=0;i<CABLE_SIZE;i++) {
        cout << computers[i];
    }
    cout << endl;
}

int main() {
    initCable();
    computers[1] = 'A';
    computers[19] = 'B';
    printCable();

    cable[1].symbol = 'A';
    for (int second = 0; second < TIME; second++) {
        this_thread::sleep_for(chrono::seconds(1));



        printCable();
    }
    return 0;
}