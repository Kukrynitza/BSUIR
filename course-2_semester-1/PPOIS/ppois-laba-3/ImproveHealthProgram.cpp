#include "ImproveHealthProgram.h"
void ImproveHealthProgram::training(){
	for (auto exercise : exercises) {
		if (exercise == "Jogging") {
			Jogging jogging;
			jogging.setHealth(health);
			jogging.setWeight(weight);
			health = jogging.getHealth();
			weight = jogging.getWeight();
		}
		if (exercise == "Gymnastics") {
			Gymnastics gymnastics;
			gymnastics.setHealth(health);
			gymnastics.setWeight(weight);
			health = gymnastics.getHealth();
			weight = gymnastics.getWeight();
		}
	}
}
void ImproveHealthProgram::eating() {
	Vegetable beetroot("свекла", 4);
	Vegetable carrot("морковь", 2);
	Vegetable onion("лук", 2);
	Meat chicken("курица", 300);
	vegetable.push_back(carrot);
	vegetable.push_back(beetroot);
	vegetable.push_back(onion);
	meat.push_back(chicken);
}
vector<Vegetable> ImproveHealthProgram::getVegetable() {
	return vegetable;
}
vector<Meat> ImproveHealthProgram::getMeat() {
	return meat;
}