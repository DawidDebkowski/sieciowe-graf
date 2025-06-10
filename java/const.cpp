#ifndef CONST
#define CONST

#include <bits/stdc++.h>

using namespace std;

const int CABLE_SIZE = 40;
const int PC_NUMBER = 5;

const char EMPTY_SYMBOL = '-';
const char CONFLICT_SYMBOL = '#';
const char JAM_SYMBOL = '!';

// CSMA/CD
const int MAX_RETRIES = 15;
const int JAM_SIGNAL_TICKS = CABLE_SIZE; // dlugosc jam

struct cablePart {
    bool right_propagation;
    bool left_propagation;
    bool distorted;
    bool changed;
    char symbol;
};

struct computer {
    int id;
    int position;
    char symbol;

    // CSMA/CD 
    int tries = 0;
    int backoffCounter = 0;   // If > 0, in backoff state
    int jamSendCounter = 0;   // If > 0, sending JAM signal

    bool isTransmitting = false;    // True if actively putting its data signal on the cable
    char messageCharToSend = EMPTY_SYMBOL; // Character of the current message being sent
    int messageSize = 0;          // Total size/duration of the current message
    int framesSentCount = 0;      // How many frames/ticks of current message sent

    int currentSignalMatrixIndex = -1; // Index in global `matrix` for the message being handled
                                       // -1 means idle or looking for a new message.
    // char prev = EMPTY_SYMBOL; // No longer used from previous logic
};

cablePart cable[CABLE_SIZE];
computer computers[PC_NUMBER];
computer printableComputers[CABLE_SIZE]; // do ładnego wypisywania

const int TIME = 10000;

struct Signal {
    int computer;
    int time;
    int size;
    char KOMUNIKAT;
    bool completed = false; // To track if this signal has been successfully sent
};

vector<Signal> matrix;

void createMatrix() {
    matrix.push_back(Signal{0, 0, 2*CABLE_SIZE, 'a', false});
    matrix.push_back(Signal{0, 900, 2*CABLE_SIZE, 'a', false});
    matrix.push_back(Signal{1, 10, 2*CABLE_SIZE, 'b', false});
    matrix.push_back(Signal{1, 300, 2*CABLE_SIZE, 'b', false});
    matrix.push_back(Signal{1, 1500, 2*CABLE_SIZE, 'b', false});
    matrix.push_back(Signal{2, 100, 2*CABLE_SIZE, 'c', false});
    matrix.push_back(Signal{2, 700, 2*CABLE_SIZE, 'c', false});
    matrix.push_back(Signal{2, 200, 2*CABLE_SIZE, 'c', false});
    matrix.push_back(Signal{2, 1500, 2*CABLE_SIZE, 'c', false});
    matrix.push_back(Signal{3, 500, 2*CABLE_SIZE, 'd', false});
    matrix.push_back(Signal{3, 400, 2*CABLE_SIZE, 'd', false});
    matrix.push_back(Signal{4, 700, 2*CABLE_SIZE, 'e', false});
}

#endif