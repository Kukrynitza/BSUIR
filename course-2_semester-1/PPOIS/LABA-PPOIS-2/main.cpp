#include <iostream>
#include "BorschtRecipe.h"
using namespace BORSCH;

int main() {
    system("chcp 1251");
    setlocale(LC_ALL, "RU");
    BorschtRecipe borsch;
    borsch.setIngridients();
    borsch.prepareIngredients();
}