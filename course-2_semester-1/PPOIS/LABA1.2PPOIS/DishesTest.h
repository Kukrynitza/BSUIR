#pragma once
#include "Dishes.h"
TEST(DishesTest, SetAndGetName) {
    Dishes dish;
    dish.setName("—уп");


    EXPECT_EQ(dish.getName(), "—уп");
}