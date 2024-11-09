#pragma once
#include <vector>
#include "Gymnastics.h"
#include "Jogging.h"
#include "Weightlifting.h"
#include "Program.h"
#include "Meat.h"
#include "Vegetable.h"
#include <string>
using namespace std;
class WeightLossProgram : public Program
{
private:
	vector<Vegetable> vegetable;
public:
	void training() override;
	void eating();
	vector<Vegetable> getVegetable();
};

