#include <stdio.h>
#include <iostream>
#include "polo.hpp"
int main(int argc, char* argv[]){
	Polo p;
	std::string service_id = p.publish_service("patatata");
	std::cout << service_id << std::endl;

	std::string patata;
	std::cin >> patata;
	if(0 != p.unpublish_service(service_id)){
		std::cout << "Something went wrong" << std::endl;
	}


	return 0;
}