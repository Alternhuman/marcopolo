#ifndef _H_NODE
#define _H_NODE

#include <string>
#include <map>

#include "parameter.h"

class Node{
public:
	std::string getAddress(){
		return this->address;
	}
	void setAddress(std::string value){
		this->address = value;
	}

	std::map<std::string, parameter> getParams(){
		return this->params;
	}
	void setParams(std::map<std::string, parameter> value){
		this->params = value;
	}

private:
	std::string address;
	std::map<std::string, parameter> params;
};

#endif