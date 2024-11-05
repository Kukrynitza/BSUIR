#pragma once
#include "Kitchen.h"
TEST(KitchenTest, AddStepsAndCook) {
    Kitchen kitchen;
    Vegetable carrot("морковь", 2);
    Meat chicken("курица", 300);

    kitchen.addStep(carrot, "clean");
    kitchen.addStep(carrot, "slice");
    kitchen.addStep(chicken, "slice");

    kitchen.setSpice("pepper");
    kitchen.setSpice("salt");
    kitchen.setDishes("кастрюля");

    kitchen.cook();

    auto carrotStates = carrot.getState();
    auto chickenStates = chicken.getState();

    ASSERT_EQ(carrotStates.size(), 2);
    EXPECT_EQ(carrotStates[0], "В количестве 2 морковь г. была почищен(а) ножом");
    EXPECT_EQ(carrotStates[1], "В количестве 2 морковь г. был(а) нарезана ножом");

    ASSERT_EQ(chickenStates.size(), 1);
    EXPECT_EQ(chickenStates[0], "В массе 300 курица г. был(а) нарезана ножом");
}