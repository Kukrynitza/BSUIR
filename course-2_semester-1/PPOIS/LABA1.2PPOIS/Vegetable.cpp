#include "Vegetable.h"
void Vegetable::setState(string state){
	this->state.push_back("В количестве " + state);
}

int Vegetable::getCount() {
	return count;
}