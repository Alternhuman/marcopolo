#include "marco.hpp"
#include "node.hpp"

int main(int argc, char* argv[]){


	Marco marco(2000);
	std::vector<Node> nodes;
	marco.marco(nodes);

	return 0;



	//Marco marco(2000);

	
	marco.marco(nodes);
	for (int i = 0; i < nodes.size(); ++i)
	{
		printf("There is a node at %s whose hostname is %s\n", nodes[i].getAddress().c_str(), nodes[i].getParams()["hostname"].value.c_str());
	}

	return 0;

	printf("%s\n", "Sending second");
	std::vector<Node> nodes2;

	Marco marco2(2000);
	marco2.marco(nodes2);
	for (int i = 0; i < nodes2.size(); ++i)
	{
		printf("Node2 %s", nodes2[i].getAddress().c_str());
	}

	std::vector<Node> nodes3;

	marco.marco(nodes3);
	for (int i = 0; i < nodes3.size(); ++i)
	{
		printf("Node2 %s", nodes3[i].getAddress().c_str());
	}

	/*marco.request_for(nodes2, "marcobootstrap");
	for (int i = 0; i < nodes2.size(); ++i)
	{
		printf("There is a node at %s whose hostname is %s\n", nodes2[i].getAddress().c_str(), nodes2[i].getParams()["hostname"].value.c_str());
	}

	std::vector<Node> nodes3, nodes4;
	int m = marco.marco(nodes3);
	if(m < 0){
		printf("%s, %d\n", "Something happened");
	}
	for (int i = 0; i < nodes3.size(); ++i)
	{
		printf("There is a node at %s whose hostname is %s\n", nodes3[i].getAddress().c_str(), nodes3[i].getParams()["hostname"].value.c_str());
	}

	marco.request_for(nodes4, "marcobootstrap");
	for (int i = 0; i < nodes4.size(); ++i)
	{
		printf("There is a node at %s whose hostname is %s\n", nodes4[i].getAddress().c_str(), nodes4[i].getParams()["hostname"].value.c_str());
	}*/
	return 0;
}