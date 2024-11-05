#pragma once
#include <iostream>
#include <string>
#include "ActionWithProduct.h"
#include "Knife.h"
using namespace std;
class Slice : public ActionWithProduct, public Knife
{
public:
	string getState() override;
};

