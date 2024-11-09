#include "Gymnastics.h"
void Gymnastics::printGymnastics() {
	cout << "Занимаемся гимнастикой" << endl << endl;
}
int Gymnastics::getHealth()
{
	return health + 2;
}
int Gymnastics::getWeight()
{
	printGymnastics();
	return weight - 2;
}