#include "Khinkali.h"
void Khinkali::setIngridients() {
    Vegetable carrot("морковь", 2);
    Vegetable onion("лук", 2);
    Meat lamb("баранина", 600);
    vegetables.emplace_back(carrot);
    vegetables.emplace_back(onion);
    meats.emplace_back(lamb);
}

void Khinkali::prepareIngredients(){
    kitchen.addStep(vegetables[0], "clean");
    kitchen.addStep(vegetables[1], "clean");
    kitchen.addStep(vegetables[1], "slice");
    kitchen.addStep(vegetables[0], "slice");
    kitchen.addStep(meats[0], "slice");
    kitchen.setSpice("pepper");
    kitchen.setDishes("сковорода");

    cout << "Рецепт хинкалей" << endl;
    for (auto meat : meats) {
        cout << meat.getName() << ' ' << meat.getWeight() << endl;
    }
    for (auto vegetable : vegetables) {
        cout << vegetable.getName() << ' ' << vegetable.getCount() << endl;
    }
    cout << endl;
    kitchen.cook();
    string states;
    for (auto meat : meats) {
        for (auto state : meat.getState()) {
            states += state + ",\n";
        }
        cout << meat.getName() << ' ' << meat.getWeight() << ": " << states << endl;
        states.clear();
    }
    for (auto vegetable : vegetables) {
        for (auto state : vegetable.getState()) {
            states += state + ",\n";
        }
        cout << vegetable.getName() << ' ' << vegetable.getCount() << ": " << states << endl;
        states.clear();
    }
    cout << endl;
}