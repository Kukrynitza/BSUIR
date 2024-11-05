#pragma once
#include "Spice.h"
class Salt : virtual public Spice {
public:
    Salt() : Spice("Соль") {}

    string getSpice();
};
