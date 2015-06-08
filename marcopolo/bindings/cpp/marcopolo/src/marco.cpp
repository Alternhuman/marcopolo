#include <rapidjson/stringbuffer.h>
#include <rapidjson/writer.h>

#include "marco.hpp"
#include "utf8.h"

#define UTF8_SEQUENCE_MAXLEN 8

Marco::Marco(int timeout, std::string group){
	this->timeout = timeout;
	this->group = group;
	this->marco_socket = socket(AF_INET, SOCK_DGRAM, 0);
	
	bzero((char *) &(this->bind_addr), sizeof(this->bind_addr));

	this->bind_addr.sin_family = AF_INET;
	this->bind_addr.sin_port = htons(PORT);
	this->bind_addr.sin_addr.s_addr = inet_addr("127.0.1.1");
	this->size_addr = sizeof(this->bind_addr);
}

std::vector<Node> Marco::marco(int max_nodes, std::vector<std::string> exclude, std::map<std::string, std::string> params, int timeout, int retries){
	rapidjson::StringBuffer s;
	rapidjson::Writer<rapidjson::StringBuffer> writer(s);

	timeout = timeout > 0 ? timeout : this->timeout;

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
	//std::wstring json_array_2(json_array_tmp.begin(), json_array_tmp.end());
	std::wstring json_array;

	json_array = std::wstring(json_array_tmp.begin(), json_array_tmp.end());

	const wchar_t *wcs = json_array.c_str();
	signed char utf8[(wcslen(wcs) + 1 /* L'\0' */) * UTF8_SEQUENCE_MAXLEN];
    char *iconv_in = (char *) wcs;
    char *iconv_out = (char *) &utf8[0];
    size_t iconv_in_bytes = (wcslen(wcs) + 1 /* L'\0' */) * sizeof(wchar_t);
    size_t iconv_out_bytes = sizeof(utf8);
    size_t ret;

    size_t b = wchar_to_utf8(wcs, iconv_in_bytes, iconv_out, iconv_out_bytes, 0);
    
    if(b < 1){
    	perror("Internal error during UTF-8 conversion");
    }

    sendto(this->marco_socket,iconv_out,(b/4)-1,0,(struct sockaddr *)&(this->bind_addr),this->size_addr);
	
	char recv_response[250];

    size_t response = recv(this->marco_socket, recv_response, 250,0);

    printf("%s\n", recv_response);

	return std::vector<Node>();

	// signed char utf8[(wcslen(wcs) + 1 /* L'\0' */) * UTF8_SEQUENCE_MAXLEN];
 //    char *iconv_in = (char *) wcs;
 //    char *iconv_out = (char *) &utf8[0];
 //    size_t iconv_in_bytes = (wcslen(wcs) + 1  L'\0' ) * sizeof(wchar_t);
 //    size_t iconv_out_bytes = sizeof(utf8);
 //    size_t ret;
    
 //    size_t b = wchar_to_utf8(wcs, iconv_in_bytes, iconv_out, iconv_out_bytes, 0);
 //    if(b < 1){
 //    	perror("Internal error during UTF-8 conversion");
 //    }

	/*sendvalue =  self.marco_socket.sendto(bytes(json.dumps({"Command": "Marco", 
                                                       "max_nodes": max_nodes,
                                                       "exclude":exclude,
                                                       "params":params,
                                                       "timeout":timeout,
                                                       "group":self.group,
                                                       "timeout":timeout}).encode('utf-8')), 
                                                       ('127.0.1.1', 1338))*/


}
