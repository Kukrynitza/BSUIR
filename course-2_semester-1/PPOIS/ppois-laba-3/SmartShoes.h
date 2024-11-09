#pragma once
#include "Wearable.h"

class SmartShoes : public Wearable {
private:
    bool gpsBe = true;
public:
    void getGPS(bool gpsBe);
    bool getGPS();
};