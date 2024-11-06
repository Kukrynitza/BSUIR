#include "Spice.h"
string Spice::getName(){
    return name;
}

void Spice::setOrigin(const string& origin) {
    this->origin = origin;
}

string Spice::getOrigin(){
    return origin;
}

void Spice::setWeight(double weight) {
    this->weight = weight;
}

double Spice::getWeight(){
    return weight;
}

void Spice::displayInfo(){
    cout << "Специя: " << name << endl;
    cout << "Происхождение: " << origin << endl;
    cout << "Вес: " << weight << " г" << endl;
}