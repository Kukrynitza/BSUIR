#pragma once
#include "Spice.h"
class Pepper : virtual public Spice {
public:
    Pepper() : Spice("Перец") {}

    string getSpice();
};
