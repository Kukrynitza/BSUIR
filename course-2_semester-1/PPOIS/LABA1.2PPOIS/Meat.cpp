#include "Meat.h"
void Meat::setState(string state){
	this->state.push_back("В массе " + state);
}

int Meat::getWeight() {
	return weight;
}