#pragma once
#include <gtest/gtest.h>
#include "User.h"
#include "Meat.h"
#include "Vegetable.h"
#include "Cloth.h"
#include "ImproveHealthProgram.h"
#include "WeightLossProgram.h"

using namespace USER;
TEST(UserTest, SetNameAndGetState) {
    User user;
    user.setName("John Doe");
    user.setWeight(75);
    user.setHealth(90);
    user.getState();
}

TEST(UserTest, SetWeight) {
    User user;
    user.setWeight(70);
    user.getState();
}
TEST(UserTest, SetHealth) {
    User user;
    user.setHealth(85);
    user.getState();
}

TEST(UserTest, EatAndCheckFood) {
    User user;
    user.setName("John Doe");

    Vegetable veg1("Carrot", 3);
    Vegetable veg2("Cucumber", 2);
    Meat meat1("Chicken", 500);
    user.setVegetable({ veg1, veg2 });
    user.setMeat({ meat1 });
    user.eat();
}

TEST(UserTest, ImproveHealthProgram) {
    User user;
    user.setWeight(70);
    user.setHealth(100);
    user.improveHealthProgram();
    user.getState();
}

TEST(UserTest, ImproveWeightLossProgram) {
    User user;
    user.setWeight(80);
    user.setHealth(90);
    user.improveWeightLossProgram();
    user.getState();
}

TEST(UserTest, GetCloth) {
    User user;
    user.getCloth();
}

TEST(UserTest, GetState) {
    User user;
    user.setName("John Doe");
    user.setWeight(75);
    user.setHealth(90);
    user.getState();
}