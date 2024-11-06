#pragma once
#include "Knife.h"
TEST(KnifeTest, SetName) {
    Knife knife;
    knife.setName("Chef's Knife");
    EXPECT_EQ(knife.getName(), "Chef's Knife") << "Knife name should be 'Chef's Knife'";
}