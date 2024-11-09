#pragma once
#include <string>
using namespace std;

class Electronics {
protected:
    string brand = "Ћуч";
    string model = "2000";
    int batteryCapacity = 2500;
public:
    string getBrand();
    string getModel();
    int getBatteryCapacity();
};

