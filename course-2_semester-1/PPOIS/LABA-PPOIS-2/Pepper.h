#pragma once
#include "Spice.h"
class Pepper : public Spice {
private:
    int spicinessLevel;
    string color;

public:
    Pepper(const string& name = "Перец", const string& origin = "", double weight = 0.0, int spicinessLevel = 0, const string& color = "")
        : Spice(name, origin, weight), spicinessLevel(spicinessLevel), color(color) {}

    void setSpicinessLevel(int level);
    int getSpicinessLevel();

    void setColor(const string& color);
    string getColor();

    string getSpice();
    void displayInfo() override;
};
