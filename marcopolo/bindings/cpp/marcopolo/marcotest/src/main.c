#include <marcopolo/marco.h>
#include <stdio.h>

int main(int argc, char* argv[]){

	marco_t mp;
	mp.timeout = 0;
	mp.group = NULL;
	node_t * nodes;
	int r = request_for(mp, "marcobootstrap", &nodes, 0, NULL, 0, NULL, 0, 1000, 0);
	int i = 0;
	for (i = 0; i < r; ++i)
	{
		fprintf(stderr, "%s\n", nodes[i].address);
	}
	return 0;
}