#pragma once
#include <iostream>
#include <string>
using namespace std;
class ActionWithProduct
{
protected:
    pair<string, int> ingridient;

public:
    void setIngridients(string name, int count);
    virtual string getState() = 0;
};

