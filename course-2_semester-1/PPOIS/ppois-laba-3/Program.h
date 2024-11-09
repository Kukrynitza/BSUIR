#pragma once
#include <string>
#include <iostream>
#include <vector>
using namespace std;
class Program
{
protected:
	int health;
	int weight;
	vector<string> exercises;
public:
	void setHealth(int health);
	void setWeight(int weight);
	void setExercise(string exercise);
	int getHealth();
	int getWeight();
	virtual void training() = 0;
};

