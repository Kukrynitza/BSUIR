#include "Dishes.h"
void Dishes::setName(const string& name) {
    this->name = name;
}

string Dishes::getName() const {
    return name;
}

void Dishes::setMaterial(const string& material) {
    this->material = material;
}

string Dishes::getMaterial() const {
    return material;
}

void Dishes::setCapacity(double capacity) {
    this->capacity = capacity;
}

double Dishes::getCapacity() const {
    return capacity;
}

void Dishes::setWeight(double weight) {
    this->weight = weight;
}

double Dishes::getWeight() const {
    return weight;
}

void Dishes::heatUp() {
    cout << "Нагреваем " << name << "..." << std::endl;
}

bool Dishes::isSuitableForInduction(){
    return material == "нержавеющая сталь" || material == "чугун";
}
void Dishes::displayInfo(){
    cout << "Посуда: " << name << endl;
    cout << "Материал: " << material << endl;
    cout << "Вместимость: " << capacity << " литров" << endl;
    cout << "Вес: " << weight << " кг" << endl;
}