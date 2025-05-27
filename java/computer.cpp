#ifndef COMPUTER
#define COMPUTER

#include "const.cpp"

void sendSignal(computer c, char KOMUNIKAT) {
    cable[c.position].symbol = KOMUNIKAT;
    cable[c.position].left_propagation = true;
    cable[c.position].right_propagation = true;
}

int collisionBreak[PC_NUMBER] = {0};

void computerBehaviour(int time) {
    for(computer c : computers) {
        if (cable[c.position].symbol == CONFLICT_SYMBOL) {
            c.jam = true;
        }

        if (c.jam) {
            
            collisionBreak[c.id]++;
        } else {
            for (Signal s : matrix) {
                if (s.computer == c.id) {
                    if(time - collisionBreak[c.id] >= s.time && time - collisionBreak[c.id] < s.time + s.size) {
                        sendSignal(computers[c.id], s.KOMUNIKAT);
                    }
                }
            }
        }
    }
}

#endif