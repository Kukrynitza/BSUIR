#pragma once
#include <string>
#include <iostream>
using namespace std;
class Exercise
{
protected:
	int health;
	int weight;
public:
	void setHealth(int health);
	void setWeight(int weight);
	virtual int getHealth() = 0;
	virtual int getWeight() = 0;
};

