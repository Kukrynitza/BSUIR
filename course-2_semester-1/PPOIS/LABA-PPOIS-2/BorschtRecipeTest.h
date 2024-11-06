#pragma once
#include "BorschtRecipe.h"
using namespace BORSCH;

TEST(BorschtRecipeTest, SetIngridientsCorrectlySetsIngredients) {
    BORSCH::BorschtRecipe recipe;
    recipe.setIngridients();

    auto vegetables = recipe.getVegetable();
    auto meats = recipe.getMeat(); 

    EXPECT_EQ(vegetables.size(), 4);
    EXPECT_EQ(meats.size(), 1); 

    EXPECT_EQ(vegetables[0].getName(), "свекла");
    EXPECT_EQ(vegetables[1].getName(), "морковь");
    EXPECT_EQ(vegetables[2].getName(), "картофель");
    EXPECT_EQ(vegetables[3].getName(), "кабачок");

    EXPECT_EQ(meats[0].getName(), "курица");
    EXPECT_EQ(meats[0].getWeight(), 300);
}

TEST(BorschtRecipeTest, PrepareIngredientsPreparesCorrectly) {
    BORSCH::BorschtRecipe recipe;
    recipe.setIngridients();
    recipe.prepareIngredients();
}