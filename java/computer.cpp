#ifndef COMPUTER
#define COMPUTER

#include "const.cpp"

void sendSignal(computer c) {
    cable[c.position].symbol = c.symbol;
    cable[c.position].left_propagatoin = true;
    cable[c.position].right_propagatoin = true;
}

void computerBehaviour(int time) {
    for(int i=0;i<PC_NUMBER;i++) {
        for (Signal s : matrix) {
            if (s.computer == i) {
                if(time >= s.time && time < s.time + s.size) {
                    sendSignal(computers[i]);
                }
            }
        }
    }
}
// csmacd
// if(cable[computers[i].id].symbol == CONFLICT_SYMBOL) {
//     // losujemy czekanie
//     // przestajemy nadawac
//     // robimy jam behaviour
// }
// if(computers[i].timer > 0) {
//             computers[i].timer--;
//         } else if( == 0)
#endif