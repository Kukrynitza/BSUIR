#include "Clean.h"
string Clean::getState(){
	return  to_string(ingridient.second) + ' ' + ingridient.first + " г. была почищен(а) " + name + "ом";
}