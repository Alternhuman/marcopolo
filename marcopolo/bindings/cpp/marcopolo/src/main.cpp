#include "marco.hpp"
#include "node.hpp"

int main(int argc, char* argv[]){
	Marco marco(2000);

	std::vector<Node> nodes = marco.marco();
	for (int i = 0; i < nodes.size(); ++i)
	{
		printf("%s\n", nodes[i].getAddress().c_str());
	}
	return 0;
}