#pragma once
#include <iostream>
#include <sstream>
#include "Recipe.h"
using namespace std;
class Khinkali : protected Recipe
{
public:
    void setIngridients() override;
    void prepareIngredients() override;
};

