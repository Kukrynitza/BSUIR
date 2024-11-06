#include <gtest/gtest.h>
#include "BorschtRecipe.h"
#include "Khinkali.h"
using namespace std;
using BORSCH::BorschtRecipe;

int main(int argc, char** argv) {
    system("chcp 1251");
    setlocale(LC_ALL, "RU");
    BorschtRecipe borscht;
    borscht.setIngridients();
    borscht.prepareIngredients();  
    Khinkali khinkali;
    khinkali.setIngridients();
    khinkali.prepareIngredients();
    //::testing::InitGoogleTest(&argc, argv);
    //return RUN_ALL_TESTS();
}