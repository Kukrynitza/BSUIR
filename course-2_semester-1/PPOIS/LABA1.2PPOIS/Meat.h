#pragma once

#include "Ingredient.h"
using namespace std;

class Meat : public Ingredient
{
private: 
	int weight;
public:
	Meat(const string& meatName, int meatWeight)
		: Ingredient(meatName), weight(meatWeight) {}
	void setState(string state) override;
	int getWeight();
};

