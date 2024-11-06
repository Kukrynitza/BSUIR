#include "Pepper.h"
void Pepper::setSpicinessLevel(int level) {
    spicinessLevel = level;
}

int Pepper::getSpicinessLevel(){
    return spicinessLevel;
}

void Pepper::setColor(const string& color) {
    this->color = color;
}

string Pepper::getColor(){
    return color;
}

string Pepper::getSpice(){
    return "Добавляем " + name + " (" + color + ")\n";
}

void Pepper::displayInfo(){
    Spice::displayInfo();
    cout << "Цвет: " << color << endl;
    cout << "Уровень остроты: " << spicinessLevel << endl;
}