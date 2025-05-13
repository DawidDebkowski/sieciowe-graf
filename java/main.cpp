#include <iostream>
#include <string>
#include <chrono>
#include <thread>

using namespace std;

const int CABLE_SIZE = 20;
const int PC_NUMBER = 3;

const char EMPTY_SYMBOL = '-';

char cable[CABLE_SIZE];
char computers[CABLE_SIZE];

void initCable() {
    for(int i=0;i<CABLE_SIZE;i++) {
        cable[i] = EMPTY_SYMBOL;
        computers[i] = ' ';
    }
}

void printCable() {
    cout << "\033[2J\033[1;1H";
    cout << "|";
    for(int i=0;i<CABLE_SIZE;i++) {
        cout << cable[i];
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
    this_thread::sleep_for(chrono::seconds(1));
    computers[17] = 'B';
    printCable();
    return 0;
}