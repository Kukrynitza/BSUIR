#pragma once
#include <string>
#include <iostream>
#include "Cloth.h"
#include "ImproveHealthProgram.h"
#include "WeightLossProgram.h"
#include "Meat.h"
#include "Vegetable.h"
using namespace std;
namespace USER {
	class User
	{
	private:
		string name;
		int weight;
		Cloth cloth;
		int health;
		vector<Vegetable> vegetable;
		vector<Meat> meat;
	public:
		void setName(string name);
		void setWeight(int weight);
		void setHealth(int health);
		void setVegetable(vector<Vegetable> vegetable);
		void setMeat(vector<Meat> meat);
		void getCloth();
		void improveHealthProgram();
		void improveWeightLossProgram();
		void eat();
		void getState();
	};
}