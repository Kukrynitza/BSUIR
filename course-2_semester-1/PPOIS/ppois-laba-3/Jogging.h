#pragma once
#include "Exercise.h"
#include <string>
#include <iostream>
using namespace std;
class Jogging : public Exercise
{
public:
	int getHealth() override;
	int getWeight() override;
	void printJogging();
};

