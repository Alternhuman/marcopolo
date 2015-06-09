#include "marco.hpp"
#include "node.hpp"

int main(int argc, char* argv[]){


	Marco marco(2000);
	std::vector<Node> nodes;
	
	
	
	int attempts = 10;

	while(attempts --> 0){

		marco.request_for(nodes, "marcobootstrap");
		for (unsigned int i = 0; i < nodes.size(); ++i)
		{
			printf("There is a node at %s\n", nodes[i].getAddress().c_str());
		}
	}

	return 0;
}