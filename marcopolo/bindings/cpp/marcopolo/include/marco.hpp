#ifndef _MARCO_HPP
#define _MARCO_HPP

#include <vector>
#include <map>
#include <string>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <strings.h>
#include <stdlib.h>
#include <stdio.h>

#include "node.hpp"

#define PORT 1338

#define STD_GROUP "224.0.0.112"

class Marco{
public:
	Marco(int timeout=1000, std::string group=STD_GROUP);
	~Marco();
	std::vector<Node> marco(int max_nodes=0, std::vector<std::string> exclude=std::vector<std::string>(), std::map<std::string, std::string> params=std::map<std::string, std::string>(), int timeout=0, int retries=0);

private:
	int marco_socket;
	struct sockaddr_in bind_addr;	
	//TODO: setters, getters
	int timeout;
	std::string group;
	socklen_t size_addr;
};


#endif