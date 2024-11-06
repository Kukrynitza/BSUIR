#pragma once
#include <iostream>
#include <vector>
#include "Kitchen.h"
#include "Vegetable.h"
#include "Meat.h"
using namespace std;
class Recipe
{
protected:
    Kitchen kitchen;
    vector<Vegetable> vegetables;
    vector<Meat> meats;
public:
    vector<Vegetable> getMeatIngridients();
    vector<Meat> getVegetableIngridients();
    virtual void setIngridients() = 0;
    virtual void prepareIngredients() = 0;
};

