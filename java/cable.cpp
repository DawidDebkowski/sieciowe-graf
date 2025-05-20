#ifndef CABLE
#define CABLE

#include "const.cpp"
#include "iostream"

using namespace std;

void initCable() {
    for(int i=0;i<CABLE_SIZE;i++) {
        cable[i] = {false, EMPTY_SYMBOL};
        computers[i] = {-1, ' '};
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
        if(computers[i].symbol != ' ') {
            cout << '|';
        } else cout << ' ';
    }
    cout << endl << ' ';
    for(int i=0;i<CABLE_SIZE;i++) {
        cout << computers[i].symbol;
    }
    cout << endl;
}

void cablePropagation() {
    for (int i = 0; i < CABLE_SIZE; i++) {
        if (cable[i].changed) {
            if (cable[i].symbol != EMPTY_SYMBOL) {
                cout << "Cable part " << i << " changed to " << cable[i].symbol << endl;
            } else {
                cout << "Cable part " << i << " is empty" << endl;
            }
        }
    }
}

#endif