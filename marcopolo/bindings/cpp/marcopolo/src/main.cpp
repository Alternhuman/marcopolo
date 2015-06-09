#include "marco.h"
#include "node.hpp"
#include <stdio.h>

int main(int argc, char* argv[]){

	marco_t mp;
	mp.timeout = 0;
	mp.group = NULL;
	node_t * nodes;
	int r = marco(mp, &nodes, 0, NULL, 0, NULL, 0, 1000, 0);

	for (int i = 0; i < r; ++i)
	{
		fprintf(stderr, "%s\n", nodes[i].address);
	}

	// Marco marco(2000);
	// std::vector<Node> nodes;

	// int attempts = 10;

	// while(attempts --> 0){

	// 	marco.request_for(nodes, "marcobootstrap");
	// 	for (unsigned int i = 0; i < nodes.size(); ++i)
	// 	{
	// 		printf("There is a node at %s\n", nodes[i].getAddress().c_str());
	// 	}
	// }

	return 0;
}