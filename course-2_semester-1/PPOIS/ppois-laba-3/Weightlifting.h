#pragma once
#include "Exercise.h"
#include <string>
#include <iostream>
using namespace std;

class Weightlifting : public Exercise
{
public:
	int getHealth() override;
	int getWeight() override;
	void printWeightlifting();
};

