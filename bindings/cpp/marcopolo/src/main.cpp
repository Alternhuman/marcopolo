#include <stdio.h>
#include <iostream>
#include "polo.hpp"
int main(int argc, char* argv[]){
	Polo p;
	std::cout << p.publish_service("patatata1212") << std::endl;
	return 0;
}