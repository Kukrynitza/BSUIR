#pragma once
#include "Salt.h"

TEST(SaltTest, SetAndGetSaltinessLevel) {
    Salt salt;
    salt.setSaltinessLevel(8);
    EXPECT_EQ(salt.getSaltinessLevel(), 8);
}

TEST(SaltTest, SetAndGetSaltType) {
    Salt salt;
    salt.setSaltType("Морская");
    EXPECT_EQ(salt.getSaltType(), "Морская");
}

TEST(SaltTest, GetSpice) {
    Salt salt("Соль", "Россия", 100.0, 5, "Морская");
    EXPECT_EQ(salt.getSpice(), "Добавляем Соль (Морская)\n");
}

TEST(SaltTest, DisplayInfo) {
    Salt salt("Соль", "Россия", 100.0, 5, "Морская");
    testing::internal::CaptureStdout();
    salt.displayInfo();
    std::string output = testing::internal::GetCapturedStdout();
    EXPECT_TRUE(output.find("Специя: Соль") != std::string::npos);
    EXPECT_TRUE(output.find("Происхождение: Россия") != std::string::npos);
    EXPECT_TRUE(output.find("Вес: 100 г") != std::string::npos);
    EXPECT_TRUE(output.find("Тип соли: Морская") != std::string::npos);
    EXPECT_TRUE(output.find("Уровень солености: 5") != std::string::npos);
}
