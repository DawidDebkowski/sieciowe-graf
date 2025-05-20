#ifndef CONST
#define CONST

#include <bits/stdc++.h>

using namespace std;

const int CABLE_SIZE = 20;
const int PC_NUMBER = 3;

const char EMPTY_SYMBOL = '-';
const char CONFLICT_SYMBOL = '#';

struct cablePart {
    bool right_propagatoin;
    bool left_propagatoin;
    bool distorted;
    bool changed;
    char symbol;
};

struct computer {
    int id;
    int position;
    char symbol;
    int timer = -1;
};

cablePart cable[CABLE_SIZE];
computer computers[PC_NUMBER];

const int TIME = 30;

struct Signal {
    int computer;
    int time;
    int size;
};

// int matrix[PC_NUMBER][TIME] = { {1, 2, 1} };
vector<Signal> matrix;

void createMatrix() {
    matrix.push_back(Signal{0, 0, 1});
    matrix.push_back(Signal{1, 2, 1});
}

#endif