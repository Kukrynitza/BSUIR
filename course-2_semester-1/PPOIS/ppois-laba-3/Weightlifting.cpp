#include "Weightlifting.h"
int Weightlifting::getHealth()
{
	return health - 1;
}
int Weightlifting::getWeight()
{
	printWeightlifting();
	return weight - 3;
}
void Weightlifting::printWeightlifting() {
	cout << "Занимаемся тяжелой атлетикой" << endl << endl;
}