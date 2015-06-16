#include <stdio.h>
#include "polo.hpp"
int main(int argc, char* argv[]){
	Polo p;
	p.publish_service("hola");
	return 0;
}