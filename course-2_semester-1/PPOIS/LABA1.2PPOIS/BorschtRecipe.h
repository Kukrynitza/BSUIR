#pragma once
#include <iostream>
#include <sstream>
#include "Recipe.h"
using namespace std;
namespace BORSCH {
    class BorschtRecipe : private Recipe
    {
    public:
        vector<Meat> getMeat();
        vector<Vegetable> getVegetable();
        void setIngridients() override;

        void prepareIngredients() override;
    };
}

