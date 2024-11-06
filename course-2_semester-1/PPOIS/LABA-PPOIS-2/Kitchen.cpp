#include "Kitchen.h"
void Kitchen::addStep(Vegetable& name, string action) {
    actionsWithVegetable.push_back(make_pair(&name, action));
}

void Kitchen::addStep(Meat& name, string action) {
    actionsWithMeat.push_back(make_pair(&name, action));
}

void Kitchen::setSpice(string spice) {
    spices.push_back(spice);
}
void Kitchen::setDishes(string dish) {
    dishes.push_back(dish);
}

void Kitchen::cook() {
    for (auto& spice : spices) {
        if (spice == "pepper") {
            Pepper pepper;
            pepper.setColor("черный");
            cout << pepper.getSpice() << endl;
        }
        if (spice == "salt") {
            Salt salt;
            cout << salt.getSpice() << endl;
        }
    }
    Dishes dish;
    for (auto& element : dishes) {
        dish.setName(element);
        cout << "Используется " << dish.getName() << endl;
    }
    for (auto& action : actionsWithMeat) {
        if (action.second == "clean") {
            Clean clean;
            clean.setIngridients(action.first->getName(), action.first->getWeight());
            clean.setName("нож");
            action.first->setState(clean.getState());
        }
        if (action.second == "slice") {
            Slice slice;
            slice.setIngridients(action.first->getName(), action.first->getWeight());
            slice.setName("нож");
            action.first->setState(slice.getState());
        }
    }

    for (auto& action : actionsWithVegetable) {
        if (action.second == "clean") {
            Clean clean;
            clean.setIngridients(action.first->getName(), action.first->getCount());
            clean.setName("нож");
            action.first->setState(clean.getState());
        }
        if (action.second == "slice") {
            Slice slice;
            slice.setIngridients(action.first->getName(), action.first->getCount());
            slice.setName("нож");
            action.first->setState(slice.getState());
        }
    }
}