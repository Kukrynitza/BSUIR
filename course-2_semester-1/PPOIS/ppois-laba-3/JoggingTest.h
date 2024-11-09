#pragma once
#include "Jogging.h"
#include <sstream>

TEST(JoggingTest, GetHealthIncreasesByOne) {
    Jogging jogging;
    jogging.setHealth(10);
    EXPECT_EQ(jogging.getHealth(), 11);
}

TEST(JoggingTest, GetWeightDecreasesByOne) {
    Jogging jogging;
    jogging.setWeight(70);
    EXPECT_EQ(jogging.getWeight(), 69);
}