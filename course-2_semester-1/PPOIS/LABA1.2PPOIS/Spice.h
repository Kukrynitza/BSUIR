#pragma once
#include <iostream>
#include <string>
using namespace std;

class Spice {
private:
    string name;
public:
    Spice(const string& name) : name(name) {}

    string getName();
};

