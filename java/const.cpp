#ifndef CONST
#define CONST

#include <bits/stdc++.h>

using namespace std;

const int CABLE_SIZE = 20;
const int PC_NUMBER = 2;

const char EMPTY_SYMBOL = '-';
const char CONFLICT_SYMBOL = '#';
const char JAM_SYMBOL = '!';

struct cablePart {
    bool right_propagation;
    bool left_propagation;
    bool distorted;
    bool changed;
    char symbol;
};

// {id, position, symbol, timer= -1 }
struct computer {
    int id;
    int position;
    char symbol;
    char jamSymbol;
    int timer = -1;
    bool jam = false;
    int tries = 0;
    char prev = EMPTY_SYMBOL;
};

cablePart cable[CABLE_SIZE];
computer computers[PC_NUMBER];
computer printableComputers[CABLE_SIZE]; // do ładnego wypisywania

const int TIME = 100;

struct Signal {
    int computer;
    int time;
    int size;
    char KOMUNIKAT;
};

vector<Signal> matrix;

void createMatrix() {
    matrix.push_back(Signal{0, 0, 2, 'a'});
    matrix.push_back(Signal{1, 2, 4, 'b'});
}

#endif