#ifndef COMPUTER
#define COMPUTER

#include "const.cpp"

void computerBehaviour() {
    for (int i = 0; i < CABLE_SIZE; i++) {
        if (computers[i].id != -1) {
            int id = computers[i].id;
            if (matrix[id] > 0) {
                int j = i + 1;
                while (j < CABLE_SIZE && cable[j].symbol != EMPTY_SYMBOL) {
                    j++;
                }
                if (j < CABLE_SIZE) {
                    cable[j].changed = true;
                    cable[j].symbol = computers[i].symbol;
                    matrix[id]--;
                }
            }
        }
    }
}

#endif