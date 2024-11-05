#pragma once
#include "Slice.h"

TEST(SliceTest, SetAndGetState) {
    Slice sliceAction;
    sliceAction.setIngridients("морковь", 150);
    sliceAction.setName("нож");
    string expectedState = "150 морковь г. был(а) нарезана ножом";
    EXPECT_EQ(sliceAction.getState(), expectedState);
}