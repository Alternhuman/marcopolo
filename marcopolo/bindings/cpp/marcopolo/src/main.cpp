#include "marco.hpp"
#include "node.hpp"

int main(int argc, char* argv[]){
	Marco marco(2000);

	std::vector<Node> nodes;
	marco.marco(nodes);
	for (int i = 0; i < nodes.size(); ++i)
	{
		printf("There is a node at %s whose hostname is %s\n", nodes[i].getAddress().c_str(), nodes[i].getParams()["hostname"].value.c_str());
	}
	return 0;
}