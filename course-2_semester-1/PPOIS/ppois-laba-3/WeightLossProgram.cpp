#include "WeightLossProgram.h"
void WeightLossProgram::training()
{
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
		if (exercise == "Weightlifting") {
			Weightlifting weightlifting;
			weightlifting.setHealth(health);
			weightlifting.setWeight(weight);
			health = weightlifting.getHealth();
			weight = weightlifting.getWeight();
		}
	}
}
void WeightLossProgram::eating() {
	Vegetable beetroot("свекла", 7);
	Vegetable carrot("морковь", 4);
	Vegetable onion("лук", 2);
	vegetable.push_back(carrot);
	vegetable.push_back(beetroot);
	vegetable.push_back(onion);
}
vector<Vegetable> WeightLossProgram::getVegetable() {
	return vegetable;
}