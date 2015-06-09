#include <rapidjson/stringbuffer.h>
#include <rapidjson/writer.h>
#include <rapidjson/document.h>
#include <iconv.h>
#include <wchar.h>

#include "marco.hpp"

#define TYPE_NULL 0
#define TYPE_FALSE 1
#define TYPE_TRUE 2
#define TYPE_OBJECT 3
#define TYPE_ARRAY 4
#define TYPE_STRING 5
#define TYPE_NUMBER 6

#define UTF8_SEQUENCE_MAXLEN 6

Marco::Marco(int timeout, std::string group){
	this->timeout = timeout;
	this->group = group;
	/*this->marco_socket = socket(AF_INET, SOCK_DGRAM, 0);


	struct timeval timeout_val;  
    if (this->timeout > 0){
        timeout_val.tv_sec = 2 * (this->timeout/1000);
        timeout_val.tv_usec = 2 * 1000 * (this->timeout % 1000);
    }
    if (setsockopt (this->marco_socket, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout_val, sizeof(timeout_val)) < 0){
        perror("setsockopt failed\n");
    }
	
	bzero((char *) &(this->bind_addr), sizeof(this->bind_addr));

	this->bind_addr.sin_family = AF_INET;
	this->bind_addr.sin_port = htons(PORT);
	this->bind_addr.sin_addr.s_addr = inet_addr("127.0.1.1");
	this->size_addr = sizeof(this->bind_addr);*/
}

Marco::~Marco(){
	close(this->marco_socket);
}

int Marco::wchar_to_utf8(wchar_t* input, char* output, size_t output_len){

	char* pi = (char*) input;
	char* po = output;
	size_t ni = wcslen(input) * sizeof(wchar_t);
	size_t no = output_len;

	iconv_t cd = iconv_open("UTF-8", "WCHAR_T");
	
	while(ni > 0) iconv(cd, &pi, &ni, &po, &no);
	
	iconv_close(cd);

	*po = 0;

	return 0;
}

int Marco::utf8_to_wchar(char* input, wchar_t* output, size_t output_len){
	//https://www.tablix.org/~avian/blog/archives/2009/10/more_about_wchar_t/
	//http://stackoverflow.com/questions/19751382/how-to-use-iconv3-to-convert-wide-string-to-utf-8
	char* pi = input;
	char* po = (char*) output;
	
	size_t ni = output_len;
	size_t no = strlen(input) * sizeof(wchar_t);

	iconv_t cd = iconv_open("WCHAR_T", "UTF-8");
	
	int iter = 0;
	int ret_count = 0;
	
	const int max_iter = 100000;
	
	while(ni > 0 && iter++ < max_iter){ 
		ret_count += iconv(cd, &pi, &ni, &po, &no);
	}
	
	iconv_close(cd);

	*po = 0;

	return ret_count;
}

int Marco::marco(std::vector<Node>& nodes, int max_nodes, std::vector<std::string> exclude, std::map<std::string, std::string> params, int timeout, int retries){
	//TODO:const char* kTypeNames[] =  { "Null", "False", "True", "Object", "Array", "String", "Number" };
		
	timeout = timeout > 0 ? timeout : this->timeout;
	
	marco_socket = socket(AF_INET, SOCK_DGRAM, 0);
	struct timeval timeout_val;  
    if (timeout > 0){
        timeout_val.tv_sec = 2 * (timeout/1000);
        timeout_val.tv_usec = 2 * 1000 * (timeout % 1000);
    }
    if (setsockopt (marco_socket, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout_val, sizeof(timeout_val)) < 0){
        perror("setsockopt failed\n");
    }
	
	bzero((char *) &(bind_addr), sizeof(bind_addr));

	bind_addr.sin_family = AF_INET;
	bind_addr.sin_port = htons(PORT);
	bind_addr.sin_addr.s_addr = inet_addr("127.0.1.1");
	size_addr = sizeof(bind_addr);


	rapidjson::StringBuffer s;
	rapidjson::Writer<rapidjson::StringBuffer> writer(s);

	
	writer.StartObject();
	writer.String("Command");
	writer.String("Marco");
	writer.String("max_nodes");
	writer.Uint(max_nodes);
	writer.String("exclude");
	writer.StartArray();
	//TODO
	writer.EndArray();
	//writer.String("params");
	//TODO
	writer.String("timeout");
	writer.Uint(timeout);
	writer.String("group");
	writer.String(this->group.c_str());
	writer.EndObject();

	std::string json_array_tmp(s.GetString());
	
	std::wstring json_array;

	json_array = std::wstring(json_array_tmp.begin(), json_array_tmp.end());

	wchar_t *wcs = (wchar_t*) json_array.c_str();
	size_t str_size = wcslen(wcs)*sizeof(wchar_t);
	int str_len = wcslen(wcs);
	char output[str_len];

	this->wchar_to_utf8(wcs, output, str_size);
    
    if(-1 == sendto(marco_socket,
    			    output,(str_len),
    			    0,
    			    (struct sockaddr *)&(bind_addr),
    			    size_addr))
    {
    	perror("Error on sending");
    	return -1;
    }
    
	char recv_response[2048];

    size_t response = recv(marco_socket, recv_response, 2048,0);
    
    if(response == (size_t)-1){
    	switch(errno){
    		case EINPROGRESS:
    		case EAGAIN:
    			perror("Timeout\n");
    			return -1;
    		default:
    			perror("Unkwnown error");
    			return -1;
    	}
    }
    
    wchar_t to_arr[response];
    char to_arr_aux[response];
    strncpy(to_arr_aux, recv_response, response);
    
    if(-1 == this->utf8_to_wchar(to_arr_aux, to_arr, response)){
    	perror("Error on conversion");
    }
	
    std::wstring ws(to_arr);
    
    std::string str(ws.begin(), ws.end());
    
    rapidjson::Document document;
    
    if(document.Parse<0>(str.c_str()).HasParseError()){
    	perror("Internal parsing error");
    	return -1;
	}
	
    assert(document.IsArray());

    std::vector<Node> return_nodes;

    for(unsigned int i= 0; i<document.Size();i++){
    	Node n;
    	n.setAddress(document[i]["Address"].GetString());

		std::map<std::string, parameter> params;
		for (rapidjson::Value::ConstMemberIterator itr = document[i]["Params"].MemberBegin(); itr != document[i]["Params"].MemberEnd(); ++itr)
		{
		    parameter p;
			p.type = itr->value.GetType();
			p.value = itr->value.GetString();
			params[itr->name.GetString()] = p;
		}
		n.setParams(params);

		
    	return_nodes.push_back(n);
    }
    nodes = return_nodes;
    close(marco_socket);
    return return_nodes.size();
}

int Marco::request_for(std::vector<Node>&nodes, std::string service, int max_nodes, std::vector<std::string> exclude, std::map<std::string, std::string> params, int timeout, int retries){
		timeout = timeout > 0 ? timeout : this->timeout;
		
		marco_socket = socket(AF_INET, SOCK_DGRAM, 0);
		
		struct timeval timeout_val;  
	    if (timeout > 0){
	        timeout_val.tv_sec = 2 * (timeout/1000);
	        timeout_val.tv_usec = 2 * 1000 * (timeout % 1000);
	    }
	    if (setsockopt (marco_socket, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout_val, sizeof(timeout_val)) < 0){
	        perror("setsockopt failed\n");
	    }
		
		bzero((char *) &(bind_addr), sizeof(bind_addr));

		bind_addr.sin_family = AF_INET;
		bind_addr.sin_port = htons(PORT);
		bind_addr.sin_addr.s_addr = inet_addr("127.0.1.1");
		size_addr = sizeof(bind_addr);


		rapidjson::StringBuffer s;
		rapidjson::Writer<rapidjson::StringBuffer> writer(s);

		
		
		writer.StartObject();
		writer.String("Command");
		writer.String("Request-for");
		writer.String("Params");
		writer.String(service.c_str());
		writer.String("max_nodes");
		writer.Uint(max_nodes);
		writer.String("exclude");
		writer.StartArray();
		//TODO
		writer.EndArray();
		//writer.String("params");
		//TODO
		writer.String("timeout");
		writer.Uint(timeout);
		writer.String("group");
		writer.String(this->group.c_str());
		writer.EndObject();

		std::string json_array_tmp(s.GetString());
	
		std::wstring json_array = std::wstring(json_array_tmp.begin(), json_array_tmp.end());

		wchar_t *wcs = (wchar_t*) json_array.c_str();
		size_t str_size = wcslen(wcs)*sizeof(wchar_t);
		int str_len = wcslen(wcs);
		char output[str_len];

		this->wchar_to_utf8(wcs, output, str_size);
	    
	    if(-1 == sendto(marco_socket,
	    			    output,str_len,
	    			    0,
	    			    (struct sockaddr *)&(bind_addr),
	    			    size_addr))
	    {
	    	perror("Error on sending");
	    	return -1;
	    }

	    char recv_response[2048];

	    size_t response = recv(marco_socket, recv_response, 2048,0);
	    
	    if(response == (size_t)-1){
	    	switch(errno){
	    		case EINPROGRESS:
	    		case EAGAIN:
	    			perror("Timeout\n");
	    			return -1;
	    		default:
	    			perror("Unkwnown error");
	    			return -1;
	    	}
	    }
	    
	    
	    
	    wchar_t to_arr[response];
	    char to_arr_aux[response];
	    strncpy(to_arr_aux, recv_response, response);
	    
	    if(-1 == this->utf8_to_wchar(to_arr_aux, to_arr, response)){
	    	perror("Error on conversion");
	    }
		
	    std::wstring ws(to_arr);
	    std::string str(ws.begin(), ws.end());
	    
	    rapidjson::Document document;
	    
	    if(document.Parse<0>(str.c_str()).HasParseError()){
	    	perror("Internal parsing error");
	    	return -1;
		}
		
	    assert(document.IsArray());

	    std::vector<Node> return_nodes;

	    for(unsigned int i= 0; i<document.Size();i++){
	    	Node n;
	    	n.setAddress(document[i]["Address"].GetString());

			std::map<std::string, parameter> params;
			for (rapidjson::Value::ConstMemberIterator itr = document[i]["Params"].MemberBegin(); itr != document[i]["Params"].MemberEnd(); ++itr)
			{
			    parameter p;
				p.type = itr->value.GetType();
				p.value = itr->value.GetString();
				params[itr->name.GetString()] = p;
			}
			n.setParams(params);

			
	    	return_nodes.push_back(n);
	    }
	    nodes = return_nodes;
	    close(marco_socket);
	    return return_nodes.size();
}