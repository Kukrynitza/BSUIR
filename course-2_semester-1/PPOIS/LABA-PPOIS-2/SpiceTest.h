#pragma once
#include <gtest/gtest.h>
#include "Spice.h"
TEST(SpiceTest, SetAndGetName) {
    Spice spice("Корица", "Цейлон", 50.0);
    EXPECT_EQ(spice.getName(), "Корица");
}

TEST(SpiceTest, SetAndGetOrigin) {
    Spice spice("Кардамон");
    spice.setOrigin("Индия");
    EXPECT_EQ(spice.getOrigin(), "Индия");
}

TEST(SpiceTest, SetAndGetWeight) {
    Spice spice("Гвоздика", "Шри-Ланка", 30.0);
    spice.setWeight(40.0);
    EXPECT_EQ(spice.getWeight(), 40.0);
}

TEST(SpiceTest, DisplayInfo) {
    Spice spice("Базилик", "Италия", 25.0);
    testing::internal::CaptureStdout();
    spice.displayInfo();
    std::string output = testing::internal::GetCapturedStdout();
    EXPECT_TRUE(output.find("Специя: Базилик") != std::string::npos);
    EXPECT_TRUE(output.find("Происхождение: Италия") != std::string::npos);
    EXPECT_TRUE(output.find("Вес: 25 г") != std::string::npos);
}