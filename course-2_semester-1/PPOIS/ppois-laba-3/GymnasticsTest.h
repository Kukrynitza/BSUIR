#pragma once
#include "Gymnastics.h"
#include <sstream>
#include <iostream>

TEST(GymnasticsTest, GetHealthIncreasesByTwo) {
    Gymnastics gymnastics;
    gymnastics.setHealth(10);
    EXPECT_EQ(gymnastics.getHealth(), 12);
}

TEST(GymnasticsTest, GetWeightDecreasesByTwo) {
    Gymnastics gymnastics;
    gymnastics.setWeight(70);
    EXPECT_EQ(gymnastics.getWeight(), 68);
}