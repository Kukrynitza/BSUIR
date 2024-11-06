#include "Salt.h"
void Salt::setSaltinessLevel(int level) {
    saltinessLevel = level;
}

int Salt::getSaltinessLevel(){
    return saltinessLevel;
}

void Salt::setSaltType(const string& type) {
    saltType = type;
}

string Salt::getSaltType(){
    return saltType;
}

string Salt::getSpice(){
    return "Добавляем " + name + " (" + saltType + ")\n";
}

void Salt::displayInfo(){
    Spice::displayInfo();
    cout << "Тип соли: " << saltType << endl;
    cout << "Уровень солености: " << saltinessLevel << endl;
}