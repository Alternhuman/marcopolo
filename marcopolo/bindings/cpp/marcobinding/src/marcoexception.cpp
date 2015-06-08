#include "marcoexception.h"
#include <stdio.h>
using namespace std;


marcoexception::marcoexception(char const* message){
	snprintf(thrownmessage, sizeof thrownmessage, message);
}

/*const char* marcoexception::what() throw(string)
{
   	return thrownmessage;
}*/