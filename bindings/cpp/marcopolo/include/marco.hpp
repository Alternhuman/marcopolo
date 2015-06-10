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
#include <unistd.h>
#include <errno.h>

#include <iostream>

#include "node.hpp"

#define PORT 1338

#define STD_GROUP "224.0.0.112"

class Marco{
public:
	Marco(int timeout=2000, std::string group=STD_GROUP);
	~Marco();
	int marco(std::vector<Node>& nodes, int max_nodes=0, std::vector<std::string> exclude=std::vector<std::string>(), std::map<std::string, parameter> params=std::map<std::string, parameter>(), int timeout=0, int retries=0);

	int request_for(std::vector<Node>& nodes, std::string service, int max_nodes=0, std::vector<std::string> exclude=std::vector<std::string>(), std::map<std::string, parameter> params=std::map<std::string, parameter>(), int timeout=0, int retries = 0);

private:
	int wchar_to_utf8(wchar_t* input, char* output, size_t output_len);
	int utf8_to_wchar(char* input, wchar_t* output, size_t output_len);
	int marco_socket;
	struct sockaddr_in bind_addr;	
	//TODO: setters, getters
	int timeout;
	std::string group;
	socklen_t size_addr;
};


#endif