#ifndef COMPUTER
#define COMPUTER

#include "const.cpp"

random_device rd;
mt19937 gen(rd());

void sendSignal(computer c, char KOMUNIKAT) {
    cable[c.position].symbol = KOMUNIKAT;
    cable[c.position].left_propagation = true;
    cable[c.position].right_propagation = true;
    cable[c.position].changed = true;
}

void computerBehaviour(int time) {
    for (int i = 0; i < PC_NUMBER; ++i) {
        computer& c = computers[i];

        // JAMMING
        if (c.jamSendCounter > 0) {
            sendSignal(c, JAM_SYMBOL);
            c.jamSendCounter--;

            // skonczony JAMMING
            if (c.jamSendCounter == 0) { 
                c.isTransmitting = false; 
                c.framesSentCount = 0;    
                c.tries++;

                if (c.tries > MAX_RETRIES) {
                    c.tries = 0;

                    // wiecej nie wysylaj
                    c.currentSignalMatrixIndex = -1; 
                } else {
                    // losowanie oczekiwania
                    uniform_int_distribution<> dis(0, (1 << min(c.tries, 10)) - 1);
                    int k = dis(gen);
                    c.backoffCounter = k * (2 * CABLE_SIZE);
                }
            }
            continue; 
        }

        // BACKOFF - przerwa po kolizji
        if (c.backoffCounter > 0) {
            c.backoffCounter--;
            continue; 
        }

        // wybór wiadomości
        if (c.currentSignalMatrixIndex == -1) {
            for (int sigIdx = 0; sigIdx < matrix.size(); sigIdx++) {
                if (matrix[sigIdx].computer == c.id && time >= matrix[sigIdx].time && !matrix[sigIdx].completed) {
                    // ustawienie wybranego sygnalu
                    c.currentSignalMatrixIndex = sigIdx;
                    c.messageCharToSend = matrix[sigIdx].KOMUNIKAT;
                    c.messageSize = matrix[sigIdx].size;
                    c.framesSentCount = 0;
                    c.tries = 0;
                    break; 
                }
            }
        }
        
        // jeśli nie wybrane - czekaj
        if (c.currentSignalMatrixIndex == -1) {
            c.isTransmitting = false;
            continue;
        }

        // COLLISION DETECTION
        if (c.isTransmitting && c.framesSentCount > 0) {
            char currentSymbolOnCable = cable[c.position].symbol;
            if (currentSymbolOnCable != EMPTY_SYMBOL && currentSymbolOnCable != c.messageCharToSend) {
                c.isTransmitting = false;
                c.jamSendCounter = JAM_SIGNAL_TICKS; 
                sendSignal(c, JAM_SYMBOL);
                c.jamSendCounter--;
                continue;
            }
        }

        // próba wysyłania
        if (cable[c.position].symbol == EMPTY_SYMBOL || cable[c.position].symbol == c.messageCharToSend) {
            c.isTransmitting = true; 
            sendSignal(c, c.messageCharToSend);
            c.framesSentCount++;

            // zakonczono wysylanie
            if (c.framesSentCount >= c.messageSize) {
                matrix[c.currentSignalMatrixIndex].completed = true;
                c.isTransmitting = false;
                c.framesSentCount = 0;
                c.tries = 0;
                c.currentSignalMatrixIndex = -1;
            }
        } else {
            c.isTransmitting = false; 
        }
    }
}

#endif