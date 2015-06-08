#include <stdio.h>
//#include "marcoexception.h"
#include "marcobinding.h"
#include <vector>

int main(){
	std::vector<string> nodes = request_for(L"deployer");

	for (int i = 0; i < nodes.size(); i++)
	{
		printf("%s\n", nodes[i].c_str());
	}
	return 0;
}