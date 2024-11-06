#pragma once
TEST(MeatTest, GetName) {
    Meat meat("Говядина", 500);
    EXPECT_EQ(meat.getName(), "Говядина");
}

TEST(MeatTest, GetWeight) {
    Meat meat("Говядина", 500);
    EXPECT_EQ(meat.getWeight(), 500);
}

TEST(MeatTest, SetAndGetState) {
    Meat meat("Говядина", 500);
    meat.setState("500 грамм");

    auto states = meat.getState();
    ASSERT_EQ(states.size(), 1);
    EXPECT_EQ(states[0], "В массе 500 грамм");
}
