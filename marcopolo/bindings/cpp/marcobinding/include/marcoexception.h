#ifndef MARCO_EX
#define MARCO_EX

#include <iostream>
#include <exception>
using namespace std;

class marcoexception : public exception
{
public:
	marcoexception(char const* message);
	//virtual char* what() throw(string) = 0;
private:
	char thrownmessage[1000];
};

#endif