#pragma once
#include "Vegetable.h"

TEST(VegetableTest, ConstructorAndGetCount) {
    Vegetable carrot("Carrot", 5);
    EXPECT_EQ(carrot.getCount(), 5);
}

TEST(VegetableTest, SetState) {
    Vegetable onion("Onion", 3);
    onion.setState("5");

    EXPECT_EQ(onion.getState().back(), "В количестве 5");
}

TEST(VegetableTest, SetStateAndGetCount) {
    Vegetable potato("Potato", 7);
    potato.setState("10");

    EXPECT_EQ(potato.getCount(), 7);
    EXPECT_EQ(potato.getState().back(), "В количестве 10");
}