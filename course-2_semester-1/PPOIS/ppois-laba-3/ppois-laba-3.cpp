#include <iostream>
#include "User.h"
using namespace USER;
using namespace std;
int main()
{
    system("chcp 1251");
    User user;
    user.setName("Толя Торпеда");
    user.setHealth(1);
    user.setWeight(148);
    user.getCloth();
    user.improveHealthProgram();
    user.eat();
    user.getState(); 
    user.improveWeightLossProgram();
    user.eat();
    user.getState();
}