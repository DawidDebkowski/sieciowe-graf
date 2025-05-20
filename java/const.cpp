#ifndef CONST
#define CONST

const int CABLE_SIZE = 20;
const int PC_NUMBER = 3;

const char EMPTY_SYMBOL = '-';
const char CONFLICT_SYMBOl = '#';

struct cablePart {
    bool right_propagatoin;
    bool left_propagatoin;
    bool distorted;
    bool changed;
    char symbol;
};

struct computer {
    int id;
    char symbol;
};

cablePart cable[CABLE_SIZE];
computer computers[CABLE_SIZE];

int matrix[PC_NUMBER] = {1, 2, 1};

const int TIME = 30;

#endif