#ifndef __H_PARAMETER
#define __H_PARAMETER

#define TYPE_NULL 0
#define TYPE_FALSE 1
#define TYPE_TRUE 2
#define TYPE_OBJECT 3
#define TYPE_ARRAY 4
#define TYPE_STRING 5
#define TYPE_NUMBER 6

typedef struct parameter{
	int type;
	std::string value;
}parameter;

#endif