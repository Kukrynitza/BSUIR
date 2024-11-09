#include "Program.h"
void Program::setHealth(int health) {
	this->health = health;
}
void Program::setWeight(int weight) {
	this->weight = weight;
}
void Program::setExercise(string exercise) {
	exercises.push_back(exercise);
}
int Program::getHealth()
{
	return health;
}
int Program::getWeight()
{
	return weight;
}