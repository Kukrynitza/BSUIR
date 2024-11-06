#pragma once
#include "Spice.h"
class Salt : public Spice {
private:
    int saltinessLevel;
    string saltType;

public:
    Salt(const string& name = "Соль", const string& origin = "", double weight = 0.0, int saltinessLevel = 0, const string& saltType = "обычная")
        : Spice(name, origin, weight), saltinessLevel(saltinessLevel), saltType(saltType) {}
    void setSaltinessLevel(int level);
    int getSaltinessLevel();
    void setSaltType(const string& type);
    string getSaltType();
    string getSpice();
    void displayInfo() override;
};
