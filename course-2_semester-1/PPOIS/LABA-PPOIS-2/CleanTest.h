#pragma once
#include "Clean.h"
TEST(CleanTest, SetAndGetState) {
    Clean cleanAction;
    cleanAction.setIngridients("картофель", 200);
    cleanAction.setName("нож");

    string expectedState = "200 картофель г. была почищен(а) ножом";
    EXPECT_EQ(cleanAction.getState(), expectedState);
}