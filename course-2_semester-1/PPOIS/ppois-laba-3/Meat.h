#pragma once
#include "Product.h"
using namespace std;

class Meat : public Product
{
private:
	int weight;
public:
	Meat(const string& meatName, int meatWeight)
		: Product(meatName), weight(meatWeight) {}
	int getWeight();
};

