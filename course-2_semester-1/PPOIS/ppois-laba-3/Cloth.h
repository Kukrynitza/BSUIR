#pragma once
#include <string>
#include <iostream>
using namespace std;
class Cloth
{
private:
    string type = "футболка";
    string size;
public:
	void setSize(string size);
    string getType();
    string getSize();
};