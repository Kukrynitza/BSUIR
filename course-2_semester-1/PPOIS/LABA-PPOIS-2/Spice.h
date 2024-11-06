#pragma once
#include <iostream>
#include <string>
using namespace std;

class Spice {
protected:
    string name;
    string origin;
    double weight;

public:
    Spice(const string& name, const string& origin = "", double weight = 0.0)
        : name(name), origin(origin), weight(weight) {}

    string getName();
    void setOrigin(const string& origin);
    string getOrigin();

    void setWeight(double weight);
    double getWeight();

    virtual void displayInfo();
};

