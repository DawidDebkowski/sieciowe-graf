#ifndef COMPUTER
#define COMPUTER

#include "const.cpp"

random_device rd;
mt19937 gen(rd());

void sendSignal(computer c, char KOMUNIKAT) {
    cable[c.position].symbol = KOMUNIKAT;
    cable[c.position].left_propagation = true;
    cable[c.position].right_propagation = true;
    cable[c.position].changed = true; // Ensure change is noted for propagation
}


/*
New computerBehaviour implements CSMA/CD:
1. Jamming: If sending JAM signal, continue until duration ends, then calculate backoff.
2. Backoff: If in backoff, countdown timer.
3. Idle/Select Message: If idle, find the next message from the matrix that is due and not completed.
4. Collision Detection (CD): If was transmitting, check if a collision occurred at its position.
   If collision, switch to Jamming state.
5. Attempt Transmission (CSMA): If no collision and cable is free, transmit one frame of the message.
   If message complete, mark as success and go to Idle.
   If cable is busy, wait (1-persistent).
*/
void computerBehaviour(int time) {
    for (int i = 0; i < PC_NUMBER; ++i) {
        computer& c = computers[i];

        // State 1: JAMMING
        if (c.jamSendCounter > 0) {
            sendSignal(c, JAM_SYMBOL);
            c.jamSendCounter--;
            if (c.jamSendCounter == 0) { // Finished JAMMING
                c.isTransmitting = false; 
                c.framesSentCount = 0;    
                c.tries++;
                if (c.tries > MAX_RETRIES) {
                    cout << "Time " << time << ": Computer " << c.symbol << " aborted message '"
                         << (c.currentSignalMatrixIndex != -1 ? matrix[c.currentSignalMatrixIndex].KOMUNIKAT : '?')
                         << "' after " << MAX_RETRIES << " retries." << endl;
                    if (c.currentSignalMatrixIndex != -1) {
                         // Optionally mark as permanently failed if needed by simulation logic
                         // matrix[c.currentSignalMatrixIndex].completed = true; // Or a new 'failed' status
                    }
                    c.tries = 0;
                    c.currentSignalMatrixIndex = -1; // Give up on this message
                } else {
                    // Enter BACKOFF state
                    uniform_int_distribution<> dis(0, (1 << min(c.tries, 10)) - 1); // k
                    int k = dis(gen);
                    c.backoffCounter = k * (2 * CABLE_SIZE); // k * slot_time (slot_time = 2 * prop_delay)
                    // cout << "Time " << time << ": Computer " << c.symbol << " backing off for " << c.backoffCounter << " ticks (tries=" << c.tries << ")" << endl;
                }
            }
            continue; 
        }

        // State 2: BACKOFF
        if (c.backoffCounter > 0) {
            c.backoffCounter--;
            continue; 
        }

        // State 3: IDLE or SELECTING MESSAGE
        if (c.currentSignalMatrixIndex == -1) { // If idle or finished previous message
            for (int sigIdx = 0; sigIdx < matrix.size(); ++sigIdx) {
                if (matrix[sigIdx].computer == c.id && time >= matrix[sigIdx].time && !matrix[sigIdx].completed) {
                    c.currentSignalMatrixIndex = sigIdx;
                    c.messageCharToSend = matrix[sigIdx].KOMUNIKAT;
                    c.messageSize = matrix[sigIdx].size;
                    c.framesSentCount = 0;
                    c.tries = 0; // Reset tries for a new message (or re-attempt of a message)
                    // cout << "Time " << time << ": Computer " << c.symbol << " selected message '" << c.messageCharToSend << "'" << endl;
                    break; 
                }
            }
        }
        
        // If no message is selected (still -1), then computer is idle for this tick.
        if (c.currentSignalMatrixIndex == -1) {
            c.isTransmitting = false; // Ensure not stuck in transmitting state if no message
            continue;
        }

        // At this point, computer has a message it wants to send/continue (c.currentSignalMatrixIndex != -1).

        // State 4: COLLISION DETECTION (if it was transmitting)
        // This check is for a computer that successfully sent a frame in the previous tick.
        if (c.isTransmitting && c.framesSentCount > 0) {
            char currentSymbolOnCable = cable[c.position].symbol;
            // Collision if cable has a foreign signal (not empty, not own signal, not JAM if we are not already jamming)
            if (currentSymbolOnCable != EMPTY_SYMBOL && currentSymbolOnCable != c.messageCharToSend) {
                 // cout << "Time " << time << ": Computer " << c.symbol << " DETECTED COLLISION! (Expected " << c.messageCharToSend << ", Got " << currentSymbolOnCable << ") while sending frame " << c.framesSentCount << "/" << c.messageSize << endl;
                c.isTransmitting = false; // Stop data transmission
                c.jamSendCounter = JAM_SIGNAL_TICKS; 
                // Send first tick of JAM immediately
                sendSignal(c, JAM_SYMBOL);
                c.jamSendCounter--;
                continue;
            }
        }

        // State 5: SENSING and ATTEMPTING TO TRANSMIT (CSMA)
        if (cable[c.position].symbol == EMPTY_SYMBOL || cable[c.position].symbol == c.messageCharToSend) { // Check if cable is free or only has our own signal (loopback)
            // Cable is free (or appears free enough to send/continue).
            c.isTransmitting = true; 
            sendSignal(c, c.messageCharToSend);
            c.framesSentCount++;

            if (c.framesSentCount >= c.messageSize) {
                // Message transmission successful!
                // cout << "Time " << time << ": Computer " << c.symbol << " successfully sent '" << c.messageCharToSend << "' (size " << c.messageSize << ")" << endl;
                if(c.currentSignalMatrixIndex != -1) matrix[c.currentSignalMatrixIndex].completed = true;
                c.isTransmitting = false;
                c.framesSentCount = 0;
                c.tries = 0;
                c.currentSignalMatrixIndex = -1; // Ready for a new message
            }
        } else {
            // Cable is busy with a foreign signal (and we weren't in the middle of transmitting, or CD would have caught it)
            // This means we wanted to start transmitting (framesSentCount == 0) but cable was busy.
            // Or, we were transmitting, but a foreign signal appeared exactly now (CD should handle this).
            // For 1-persistent: do nothing, will try again next tick.
            c.isTransmitting = false; 
            // cout << "Time " << time << ": Computer " << c.symbol << " found cable busy (symbol: " << cable[c.position].symbol << "), will wait." << endl;
        }
    }
}

#endif