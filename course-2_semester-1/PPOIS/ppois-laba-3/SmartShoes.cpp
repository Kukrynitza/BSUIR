#include "SmartShoes.h"
void SmartShoes::getGPS(bool gpsBe) {
    this->gpsBe = gpsBe;
}
bool SmartShoes::getGPS() {
    return gpsBe;
}