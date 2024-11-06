#pragma once
#include "Pepper.h"

TEST(PepperTest, SetAndGetSpicinessLevel) {
    Pepper pepper;
    pepper.setSpicinessLevel(5);
    EXPECT_EQ(pepper.getSpicinessLevel(), 5);
}

TEST(PepperTest, SetAndGetColor) {
    Pepper pepper;
    pepper.setColor("Красный");
    EXPECT_EQ(pepper.getColor(), "Красный");
}

TEST(PepperTest, GetSpice) {
    Pepper pepper("Перец", "Мексика", 40.0, 7, "Красный");
    EXPECT_EQ(pepper.getSpice(), "Добавляем Перец (Красный)\n");
}

TEST(PepperTest, DisplayInfo) {
    Pepper pepper("Перец", "Мексика", 40.0, 7, "Красный");
    testing::internal::CaptureStdout();
    pepper.displayInfo();
    std::string output = testing::internal::GetCapturedStdout();
    EXPECT_TRUE(output.find("Специя: Перец") != std::string::npos);
    EXPECT_TRUE(output.find("Происхождение: Мексика") != std::string::npos);
    EXPECT_TRUE(output.find("Вес: 40 г") != std::string::npos);
    EXPECT_TRUE(output.find("Цвет: Красный") != std::string::npos);
    EXPECT_TRUE(output.find("Уровень остроты: 7") != std::string::npos);
}