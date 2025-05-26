#ifndef CABLE
#define CABLE

#include "const.cpp"
// #include "iostream"

using namespace std;

ofstream saveFile;

void initCable() {
    for(int i=0;i<CABLE_SIZE;i++) {
        cable[i] = {false, false, false, false, EMPTY_SYMBOL};
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
        if(printableComputers[i].symbol != ' ') {
            cout << '|';
        } else cout << ' ';
    }
    cout << endl << ' ';
    for(int i=0;i<CABLE_SIZE;i++) {
        cout << printableComputers[i].symbol;
    }
    cout << endl;
}

// tworzy cudowną tablice komputerów do wypisywania
void createPrintableComputers() {
    for(int i=0;i<CABLE_SIZE;i++) {
        printableComputers[i] = computer{i, i, ' '};
    }

    for(int i=0;i<PC_NUMBER;i++) {
        printableComputers[computers[i].position] = computers[i];
    }
}

// do wywołania tylko po ustawieniu komputerów
void initSavefile(string filepath) {
    saveFile = ofstream(filepath);
    if (saveFile.is_open()) {
        saveFile << "abc";
        saveFile.close();
    }
}

void saveCable() {

}

void cablePropagation() {
    cablePart newCable[CABLE_SIZE];
    for (int i = 0; i < CABLE_SIZE; i++) {
        newCable[i] = {false, false, false, false, EMPTY_SYMBOL};
    }
    for (int i = 0; i < CABLE_SIZE; i++) {
        if (cable[i].symbol != EMPTY_SYMBOL) {
            if(cable[i].left_propagation && i > 0){
                if(cable[i-1].symbol != EMPTY_SYMBOL && cable[i-1].right_propagation) {
                    newCable[i-1].symbol = CONFLICT_SYMBOL;
                    newCable[i-1].changed = true;
                    newCable[i-1].left_propagation = true;
                    newCable[i-1].distorted = true;
                } else {
                    if(newCable[i-1].symbol != EMPTY_SYMBOL) {
                        newCable[i-1].symbol = CONFLICT_SYMBOL;
                    } else {
                        newCable[i-1].symbol = cable[i].symbol;
                    }
                    newCable[i-1].left_propagation = true;
                    newCable[i-1].changed = true;
                }
            }
            if(cable[i].right_propagation && i < CABLE_SIZE - 1){
                if(cable[i+1].symbol != EMPTY_SYMBOL && cable[i+1].left_propagation) {
                    newCable[i+1].symbol = CONFLICT_SYMBOL;
                    newCable[i+1].changed = true;
                    newCable[i+1].right_propagation = true;
                    newCable[i+1].distorted = true;
                } else {
                    if(newCable[i+1].symbol != EMPTY_SYMBOL) {
                        newCable[i+1].symbol = CONFLICT_SYMBOL;
                    } else {
                        newCable[i+1].symbol = cable[i].symbol;
                    }
                    newCable[i+1].right_propagation = true;
                    newCable[i+1].changed = true;
                }
            }
            if(i+1 == CABLE_SIZE) {
                newCable[i].right_propagation = false;
            }
            if(i == 0) {
                newCable[i].left_propagation = false;
            }
        }
    }
    for (int i = 0; i < CABLE_SIZE; i++) {
        cable[i] = newCable[i];
    }
}

#endif