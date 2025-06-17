#ifndef CONST
#define CONST

#include <bits/stdc++.h>

using namespace std;

const int CABLE_SIZE = 80;
const int PC_NUMBER = 3;

const char EMPTY_SYMBOL = '-';
const char CONFLICT_SYMBOL = '#';
const char JAM_SYMBOL = '#';

// CSMA/CD
const int MAX_RETRIES = 15;
const int JAM_SIGNAL_TICKS = CABLE_SIZE; // długość sygnału JAM

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
    int backoffCounter = 0;   // Jeśli > 0, komputer jest w stanie backoff
    int jamSendCounter = 0;   // Jeśli > 0, komputer wysyła sygnał JAM

    bool isTransmitting = false;    // True jeśli komputer aktywnie wysyła dane na kabel
    char messageCharToSend = EMPTY_SYMBOL; // Znak aktualnie wysyłanej wiadomości
    int messageSize = 0;          // Całkowity rozmiar/długość wiadomości
    int framesSentCount = 0;      // Liczba wysłanych ramek(ticków) bieżącej wiadomości

    int currentSignalMatrixIndex = -1; // Indeks w globalnej macierzy `matrix` dla obsługiwanej wiadomości
                                       // -1 oznacza bezczynność lub oczekiwanie na nową wiadomość.
    // char prev = EMPTY_SYMBOL; // Już nieużywane z poprzedniej logiki
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
    bool completed = false; // Czy sygnał został już wysłany poprawnie
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
    // matrix.push_back(Signal{3, 500, 2*CABLE_SIZE, 'd', false});
    // matrix.push_back(Signal{3, 400, 2*CABLE_SIZE, 'd', false});
    // matrix.push_back(Signal{4, 700, 2*CABLE_SIZE, 'e', false});
}

#endif