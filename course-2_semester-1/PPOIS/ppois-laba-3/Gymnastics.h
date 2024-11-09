#pragma once
#include "Exercise.h"
#include <string>
#include <iostream>
using namespace std;
class Gymnastics : public Exercise
{
public:
	void printGymnastics();
	int getHealth() override;
	int getWeight() override;
};

