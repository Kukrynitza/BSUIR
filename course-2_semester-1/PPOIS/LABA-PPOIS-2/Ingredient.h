#pragma once
#include <iostream>
#include <vector>
#include <string>
#include <sstream> 
using namespace std;

class Ingredient
{
protected:
	string name;
	vector<string> state;
public:
	Ingredient(const string& name) : name(name) {}
	virtual void setState(string state) = 0;
	vector<string> getState();
	string getName();
};

