#pragma once
#include <iostream>
#include <vector>
#include <string>
#include "Vegetable.h"
#include "Slice.h"
#include "Meat.h"
#include "Clean.h"
#include "Pepper.h"
#include "Salt.h"
#include "Dishes.h"
using namespace std;

class Kitchen
{
private:
    vector<pair<Meat*, string>> actionsWithMeat;
    vector<pair<Vegetable*, string>> actionsWithVegetable;
    vector<string> spices;
    vector<string> dishes;


public:
    void addStep(Vegetable& name, string action);
    void addStep(Meat& name, string action);
    void setSpice(string spice);
    void setDishes(string dish);
    void cook();
};
