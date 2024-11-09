#pragma once
#include <vector>
#include "Gymnastics.h"
#include "Jogging.h"
#include "Program.h"
#include "Meat.h"
#include "Vegetable.h"
#include <string>
using namespace std;
class ImproveHealthProgram : public Program
{
private:
	vector<Vegetable> vegetable;
	vector<Meat> meat;
public:
	void training() override;
	void eating();
	vector<Vegetable> getVegetable();
	vector<Meat> getMeat();
};

