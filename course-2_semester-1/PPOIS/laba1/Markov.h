#pragma once
#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
#include <string>
#include <math.h>
#include <iomanip>
#include <map>
#include <sstream>
#include "ReadInformationFromFile.h"
#include <list>


class Markov {
private:
    string text;
    list<pair<string, string>> changes;
public:
    void getText(string text);
    void getChanges(list<pair<string, string>> changes);
    string setText();
    list<pair<string, string>> setChanges();
    void applicationofmarkovalgorithms();

};

//C:\Users\37533\Desktop\course-2_semester-1\PPOIS\laba1\PPOIS-laba-1.txt