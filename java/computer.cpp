#ifndef COMPUTER
#define COMPUTER

#include "const.cpp"

random_device rd;
mt19937 gen(rd());

void sendSignal(computer c, char KOMUNIKAT) {
    cable[c.position].symbol = KOMUNIKAT;
    cable[c.position].left_propagation = true;
    cable[c.position].right_propagation = true;
}

int collisionBreak[PC_NUMBER] = {0};
Signal lastSent[PC_NUMBER];


/*
Po pierwsze, jak będzie JAM po raz drugi to zepsuliśmy już size naszego sygnału!
Po drugie previous nie działa najlepiej
Po trzecie tries też nie działa najlepiej

Dużo podstawowych błędów które nie wiem jak naprawić, myślę, że trzeba wejść na miro i rozpisać diagram zachowania
komputera i tyle, a potem to zakodować nie ma innej opcji
*/

void computerBehaviour(int time) {
    for(computer& c : computers) {
        cout << c.symbol << " " << c.prev << " " << cable[c.position].symbol << "\n";
        if (c.prev == CONFLICT_SYMBOL && cable[c.position].symbol != CONFLICT_SYMBOL) {
            c.jam = true;
            // sendSignal(computers[c.id], JAM_SYMBOL);
            c.tries++;
        }
        // if (cable[c.position].symbol == CONFLICT_SYMBOL) {
        //     c.jam = true;
        // }
        // if(cable[c.position].symbol == EMPTY_SYMBOL && c.jam){
        //     sendSignal(computers[c.id], JAM_SYMBOL);
        //     c.tries++;
        // }
        c.prev = cable[c.position].symbol;

        if (c.jam) {
            if (c.timer == -1) {
                uniform_int_distribution<> dis(1, int (pow(2, c.tries+1)));
                c.timer = dis(gen) * 2 * CABLE_SIZE;
            } else {
                if (c.timer == 0) {
                    if (lastSent[c.id].size != 0) {
                        sendSignal(c, lastSent[c.id].KOMUNIKAT);
                        lastSent[c.id].size--;
                    } else {
                        c.jam = false;
                        c.timer--;
                    }              
                } else {
                    c.timer--;
                }
            }

            collisionBreak[c.id]++;
        } else {
            for (Signal s : matrix) {
                if (s.computer == c.id) {
                    if(time - collisionBreak[c.id] >= s.time && time - collisionBreak[c.id] < s.time + s.size) {
                        sendSignal(computers[c.id], s.KOMUNIKAT);
                        lastSent[c.id] = s;
                    }
                }
            }
        }

    }
}

#endif