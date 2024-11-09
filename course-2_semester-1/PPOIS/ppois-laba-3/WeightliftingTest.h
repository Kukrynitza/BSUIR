#pragma once
#include "Weightlifting.h"
#include <sstream>

TEST(WeightliftingTest, GetHealthDecreasesByOne) {
    Weightlifting weightlifting;
    weightlifting.setHealth(10);
    EXPECT_EQ(weightlifting.getHealth(), 9);
}

TEST(WeightliftingTest, GetWeightDecreasesByThree) {
    Weightlifting weightlifting;
    weightlifting.setWeight(70);
    EXPECT_EQ(weightlifting.getWeight(), 67);
}