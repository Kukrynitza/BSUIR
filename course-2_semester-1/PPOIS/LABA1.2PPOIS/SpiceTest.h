#pragma once
#include <gtest/gtest.h>
#include "Spice.h"
TEST(SpiceTest, GetName) {
    Spice spice("Корица");
    EXPECT_EQ(spice.getName(), "Корица");
}