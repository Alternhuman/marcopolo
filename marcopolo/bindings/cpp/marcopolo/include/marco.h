typedef struct marco_t{
	int timeout;
	char* group;
}marco_t;

typedef struct parameter_t{
	char* name;
	int type;
	char* value;
}parameter_t;

typedef struct node_t{
	char* address;
	parameter_t* params;
}node_t;

extern "C"{
	int marco(marco_t mp, node_t** nodes, int max_nodes, char* exclude[], int exclude_len, parameter_t* params, int params_len, int timeout, int retries);
	int request_for(marco_t mp, char* service, node_t** nodes, int max_nodes, char* exclude[], int exclude_len, parameter_t* params, int params_len, int timeout, int retries);
}