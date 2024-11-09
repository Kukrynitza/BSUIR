#pragma once
#pragma once
#include <iostream>
#include <vector>
#include <string>
#include <sstream> 
using namespace std;

class Product
{
protected:
	string name;
public:
	Product(const string& name) : name(name) {}
	string getName();
};

