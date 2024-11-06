#pragma once
#include <string>
#include <iostream>
using namespace std;

class Dishes
{
private:
    string name;
    string material;
    double capacity;
    double weight; 

public:
    void setName(const string& name);
    string getName() const;

    void setMaterial(const string& material);
    string getMaterial() const;

    void setCapacity(double capacity);
    double getCapacity() const;

    void setWeight(double weight);
    double getWeight() const;

    void heatUp();
    bool isSuitableForInduction();
    void displayInfo();
};