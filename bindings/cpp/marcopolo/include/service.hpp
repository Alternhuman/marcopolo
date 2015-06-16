#ifndef _HPP_SERVICE
#define _HPP_SERVICE

#include <string>
#include <map>
#include "node.hpp"


class Service{
public:
	std::string getID(){
		return this->id;
	}

	std::map<std::string, parameter> getParams(){
		return this->params;
	}


private:
	std::string id;
	std::map<std::string, parameter> params;
	std::vector<std::string> multicast_groups;
	bool enabled;
};

#endif