#pragma once
#include "Product.h"
using namespace std;
class Vegetable : public Product
{
private:
	int count;
public:
	Vegetable(const string& vegName, int vegWeight)
		: Product(vegName), count(vegWeight) {}
	int getCount();
};
