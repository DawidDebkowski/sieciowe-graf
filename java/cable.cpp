#ifndef CABLE
#define CABLE

#include "const.cpp"
#include "iostream"

using namespace std;

void initCable() {
    for(int i=0;i<CABLE_SIZE;i++) {
        cable[i] = {false, false, false, false, EMPTY_SYMBOL};
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
    cablePart newCable[CABLE_SIZE];
    for (int i = 0; i < CABLE_SIZE; i++) {
        newCable[i] = {false, false, false, false, EMPTY_SYMBOL};
    }
    for (int i = 0; i < CABLE_SIZE; i++) {
        if (cable[i].symbol != EMPTY_SYMBOL) {
            if(cable[i].left_propagatoin && i > 0){
                if(cable[i-1].symbol != EMPTY_SYMBOL && cable[i-1].right_propagatoin) {
                    newCable[i-1].symbol = CONFLICT_SYMBOl;
                    newCable[i-1].changed = true;
                } else {
                    newCable[i-1].symbol = cable[i].symbol;
                    newCable[i-1].left_propagatoin = true;
                    newCable[i-1].changed = true;
                }
            }
            if(cable[i].right_propagatoin && i < CABLE_SIZE - 1){
                if(cable[i+1].symbol != EMPTY_SYMBOL && cable[i+1].left_propagatoin) {
                    newCable[i+1].symbol = CONFLICT_SYMBOl;
                    newCable[i+1].changed = true;
                } else {
                    newCable[i+1].symbol = cable[i].symbol;
                    newCable[i+1].right_propagatoin = true;
                    newCable[i+1].changed = true;
                }
            }
            if(i+1 == CABLE_SIZE) {
                newCable[i].right_propagatoin = false;
            }
            if(i == 0) {
                newCable[i].left_propagatoin = false;
            }
        }
    }
    for (int i = 0; i < CABLE_SIZE; i++) {
        cable[i] = newCable[i];
    }
}

#endif