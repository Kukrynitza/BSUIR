#pragma once
#include "Ingredient.h"
using namespace std;
class Vegetable : public Ingredient
{
private:
	int count;
public:
	Vegetable(const string& vegName, int vegWeight)
		: Ingredient(vegName), count(vegWeight) {}

	void setState(string state) override;
	int getCount();
};

