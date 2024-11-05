#pragma once
#include "Salt.h"

TEST(SaltTest, GetName) {
    Salt salt;
    EXPECT_EQ(salt.getName(), "Соль");
}

TEST(SaltTest, GetSpice) {
    Salt salt;
    EXPECT_EQ(salt.getSpice(), "Добавляем Соль\n");
}
