#include <gtest/gtest.h>
#include "CleanTest.h"
#include "PepperTest.h"
#include "DishesTest.h"
#include "KnifeTest.h"
#include "SpiceTest.h"
#include "SliceTest.h"
#include "ActionWithProduct.h"
#include "Ingredient.h"
#include "Khinkali.h"
#include "BorschtRecipeTest.h"
#include "MeatTest.h"
#include "SaltTest.h"
#include "VegetableTest.h"
#include "Recipe.h"
#include "KitchenTest.h"

int main(int argc, char** argv) {
    system("chcp 1251");
    setlocale(LC_ALL, "RU");
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

//OpenCppCoverage --sources LABA-PPOIS-2 -- .\x64\Debug\LABA-PPOIS-2.exe