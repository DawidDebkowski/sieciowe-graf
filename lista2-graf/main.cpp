#include <iostream>
#include <string>
#include <chrono>
#include <thread>

using namespace std;

const int CABLE_SIZE = 20;
const int PC_NUMBER = 3;

const char EMPTY_SYMBOL = '-';
const char CONFLICT_SYMBOl = '#';

struct cablePart {
    bool changed;
    char symbol;
};

// dla komputerów ' ' id jest -1
// dla reszty id po kolei od 0 do PC_NUMBER
// zeby działała macierz natężeń
struct computer {
    int id;
    char symbol;
};

cablePart cable[CABLE_SIZE];
computer computers[CABLE_SIZE];

// ile komunikatów chce wysłać komputer o danym id
int matrix[PC_NUMBER] = {1, 2, 1};

const int TIME = 30;

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

int main() {
    initCable();
    computers[1] = {0, 'A'};
    computers[19] = {1, 'B'};
    printCable();

    cable[1].symbol = 'A';
    cable[19].symbol = 'B';
    for (int second = 0; second < TIME; second++) {
        this_thread::sleep_for(chrono::seconds(1));

        for (int i = 0; i < CABLE_SIZE; i++) {
            cable[i].changed = false;
        }

        for (int i = 0; i < CABLE_SIZE; i++) {
            if (cable[i-1].symbol != EMPTY_SYMBOL && cable[i+1].symbol != EMPTY_SYMBOL && cable[i-1].symbol != cable[i+1].symbol) {
                cable[i].symbol = CONFLICT_SYMBOl;
                cable[i].changed = true;
            }

            if (cable[i].symbol == CONFLICT_SYMBOl && !cable[i].changed) {
                try {
                    cable[i-1] = {true, CONFLICT_SYMBOl};
                } catch (exception e) {}
                try {
                    cable[i+1] = {true, CONFLICT_SYMBOl};
                } catch (exception e) {}
            } else if (cable[i].symbol != EMPTY_SYMBOL && !cable[i].changed) {
                try {
                    cable[i-1] = {true, cable[i].symbol};
                } catch (exception e) {}
                try {
                    cable[i+1] = {true, cable[i].symbol};
                } catch (exception e) {}
            }
        }

        printCable();
    }

    return 0;
}