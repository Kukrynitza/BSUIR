#include "User.h"
using namespace USER;
void User::setName(string name) {
	this->name = name;
}
void User::setWeight(int weight) {
	this->weight = weight;
}
void User::setHealth(int health) {
	this->health = health;
}

void User::setVegetable(vector<Vegetable> vegetable) {
	this->vegetable = vegetable;
}
void User::setMeat(vector<Meat> meat) {
	this->meat = meat;
}
void User::getCloth() {
	cloth.setSize("М");
	cout << cloth.getSize() << ' ' << cloth.getType() << endl << endl;
}
void User::improveHealthProgram() {
	ImproveHealthProgram program;
	program.setHealth(health);
	program.setWeight(weight);
	program.setExercise("Jogging");
	program.setExercise("Gymnastics");
	program.setExercise("Gymnastics");
	program.setExercise("Gymnastics");
	program.setExercise("Jogging");
	program.training();
	health = program.getHealth();
	weight = program.getWeight();
	program.eating();
	setVegetable(program.getVegetable());
	setMeat(program.getMeat());
}
void User::improveWeightLossProgram() {
	WeightLossProgram program;
	program.setHealth(health);
	program.setWeight(weight);
	program.setExercise("Weightlifting");
	program.setExercise("Weightlifting");
	program.setExercise("Gymnastics");
	program.setExercise("Gymnastics");
	program.setExercise("Weightlifting");
	program.setExercise("Jogging");
	program.setExercise("Jogging");
	program.training();
	health = program.getHealth();
	weight = program.getWeight();
	program.eating();
	setVegetable(program.getVegetable());
}
void User::eat() {
	cout << name << " Съел: " << endl;
	for (auto vegetables : vegetable) {
		cout << vegetables.getName() << ' ' << vegetables.getCount() << endl;
	}
	for (auto meats : meat) {
		cout << meats.getName() << ' ' << meats.getWeight() << endl;
	}
	cout << endl << endl;
}
void User::getState() {
	cout << name << " Вес: " << weight << " Оценка состояния здоровья: " << health << endl << endl;
}