#pragma once
#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
#include <string>
#include <math.h>
#include <iomanip>
#include <map>
#include <list>
#include <sstream>
using namespace std;

class Recording {
private:
    string text, rec;
    list<pair<string, string>> changes;
public:
    void getRecord(string rec);
    void getChanges(list<pair<string, string>> changes);
    list<pair<string, string>> setChanges();
    void getText(string text);
    string setText();
    string setRecord();
    bool recordingInformationFromFile();
};