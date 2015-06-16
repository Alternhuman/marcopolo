#include "polo.hpp"
#include <stdio.h>

#include <openssl/bio.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/pem.h>
#include <openssl/x509.h>
#include <openssl/x509_vfy.h>
#include <openssl/evp.h>

#include <stdio.h>
#include <strings.h>
#include <string.h>
#include <sys/socket.h>
#include <stdio.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <rapidjson/stringbuffer.h>
#include <rapidjson/writer.h>
#include <rapidjson/document.h>
#include <string>

#include <pwd.h>
#include <unistd.h>
#include <fstream>
#include <iostream>
//#include <sys/types.h>


#define PORT 1390
#define ADDRESS "127.0.0.1"

Polo::Polo(int timeout){
    /*TODO  self.polo_socket.settimeout(TIMEOUT/1000.0)*/


    const SSL_METHOD *method;
    SSL_CTX *ctx;
    SSL *ssl;

    OpenSSL_add_all_algorithms();
    ERR_load_BIO_strings();
    ERR_load_crypto_strings();
    SSL_load_error_strings();

    if(SSL_library_init() < 0)
        perror("Could not initialize the OpenSSL library !\n");

    method = SSLv23_client_method();
    if ( (ctx = SSL_CTX_new(method)) == NULL)
        perror("Unable to create a new SSL context structure.\n");

    ssl = SSL_new(ctx);

    this->polo_socket = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in poloserver;
    size_t size_addr = sizeof(poloserver);

    if (this->polo_socket < 0){
        perror("Internal error when opening connection to Marco");
    }

    bzero((char *) &poloserver, sizeof(poloserver));

    poloserver.sin_family = AF_INET;
    poloserver.sin_port = htons(PORT);
    poloserver.sin_addr.s_addr = inet_addr(ADDRESS);

    if(-1 == connect(this->polo_socket, (sockaddr*)&poloserver, size_addr)){
        perror("Fail");
    }

    SSL_set_fd(ssl, this->polo_socket);

    if ( SSL_connect(ssl) != 1 )
        perror("Error: Could not build a SSL session");
    
    this->wrappedSocket = ssl;

    /*SSL_write(ssl, "Hola", sizeof("Hola"));
    char buf_recv[500];
    SSL_read(ssl, buf_recv, 500);

    
    printf("%s\n", buf_recv);*/
}

Polo::~Polo(){
    SSL_shutdown(this->wrappedSocket);
    shutdown(this->polo_socket, 2);
}

std::string Polo::publish_service(std::string service, std::vector<std::string> multicast_groups, bool permanent, bool root){
    std::string token = this->get_token();
    std::cout << token << std::endl;
    return "";

    if(service.length() <= 1){
        throw PoloException("The name of the service" + service+ "is invalid");
    }

    std::string reason;
    for (std::vector<std::string>::iterator it = multicast_groups.begin();
         it != multicast_groups.end(); 
         it++)
    {
        if(0 != this->verify_ip(*it, reason)){
            throw PoloException(reason);
        }
    }

    rapidjson::StringBuffer stringbuffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(stringbuffer);

    writer.StartObject();
    writer.String("Command");
    writer.String("Register");

    writer.String("Args");
    writer.StartObject();
    writer.String("token");
    writer.String(token.c_str());
    writer.String("service");
    writer.String(service.c_str());
    writer.String("multicast_groups");
    writer.StartArray();
    for (std::vector<std::string>::iterator it = multicast_groups.begin(); 
        it != multicast_groups.end();
        it++){
        writer.String((*it).c_str());
    }
    writer.EndArray();
    writer.String("permanent");
    writer.Bool(permanent);
    writer.String("root");
    writer.Bool(root);
    writer.EndObject();
    writer.EndObject();
    
    std::string json_array_tmp = stringbuffer.GetString();
    std::wstring json_array;

    json_array = std::wstring(json_array_tmp.begin(), json_array_tmp.end());
    if(json_array.length() == 0){
        throw PoloException("Error in JSON encoder");
    }
    wchar_t *wcs = (wchar_t*) json_array.c_str();
    size_t str_size = wcslen(wcs)*sizeof(wchar_t);
    int str_len = wcslen(wcs);
    char output[str_len];

    wchar_to_utf8(wcs, output, str_size);
    //TODO: watch length

    SSL_write(this->wrappedSocket, output, str_size);

    char recv_response[2048];

    size_t response = SSL_read(this->wrappedSocket, recv_response, 2048);
    if(response != 0){
        switch(SSL_get_error(this->wrappedSocket, response)){
            case SSL_ERROR_ZERO_RETURN:
                perror("The TLS/SSL connection has been closed");
                break;
            case SSL_ERROR_WANT_READ:
            case SSL_ERROR_WANT_WRITE:
                perror("WANT_WRITE");
                break;
            case SSL_ERROR_WANT_CONNECT:
            case SSL_ERROR_WANT_ACCEPT:
                perror("The operation did not complete");
                break;
            case SSL_ERROR_SYSCALL:
                perror("I/O error");
                break;
            case SSL_ERROR_SSL:
                perror("Failure in the SSL library");
                break;
            default:
                perror("Unknown error");
                break;
        }
    }

    wchar_t to_arr[response];
    char to_arr_aux[response];
    strncpy(to_arr_aux, recv_response, response);
    
    if(-1 == utf8_to_wchar(to_arr_aux, to_arr, response)){
        perror("Error on conversion");
    }
    
    std::wstring ws(to_arr);
    
    std::string str(ws.begin(), ws.end());
    
    rapidjson::Document document;
    
    if(document.Parse<0>(str.c_str()).HasParseError()){
        perror("Internal parsing error");
    }
    
    assert(document.IsObject());

    if(document["Error"] != document.Size()){
        perror(std::string(document["Error"].GetString()).c_str());
        throw PoloException("Error in publishing");
    }

    return document["OK"].GetString();
}

std::string Polo::get_token(){
    uid_t uid = geteuid();
    struct passwd *pw_user = getpwuid(uid);
    char dir[strlen(pw_user->pw_dir)+strlen("/.polo/token")];
    dir[0] = '\0';
    strcat(dir, pw_user->pw_dir);
    strcat(dir, "/.polo/token");

    std::ifstream infile(dir);
    std::string token;
    if(!infile.good()){
        token = this->request_token(pw_user);
        if(token.length() == 0)    return "";
        
    }

    FILE *f = fopen(dir, "r");
    if(f == NULL)
        perror(dir);

    char read_buffer[50];
    if(NULL == fgets(read_buffer, 50, f)){
        return "";
    }
    return std::string(read_buffer);

}

std::string Polo::request_token(const struct passwd *pw_user){
    rapidjson::StringBuffer stringbuffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(stringbuffer);
    
    writer.StartObject();
    writer.String("Command");
    writer.String("Request-token");
    writer.String("Args");
    writer.StartObject();
    writer.String("uid");
    writer.Uint(geteuid());
    writer.EndObject();
    writer.EndObject();

    //TODO: avoid redundancy (this snippet is written 3 times at least!)
    std::string json_array_tmp = stringbuffer.GetString();
    std::wstring json_array;

    json_array = std::wstring(json_array_tmp.begin(), json_array_tmp.end());
    if(json_array.length() == 0){
        throw PoloException("Error in JSON encoder");
    }
    wchar_t *wcs = (wchar_t*) json_array.c_str();
    size_t str_size = wcslen(wcs)*sizeof(wchar_t);
    int str_len = wcslen(wcs);
    char output[str_len];

    wchar_to_utf8(wcs, output, str_size);
    //TODO: watch length

    SSL_write(this->wrappedSocket, output, str_len);
    
    char recv_response[2048];

    size_t response = SSL_read(this->wrappedSocket, recv_response, 2048);

    wchar_t to_arr[response];
    char to_arr_aux[response];
    strncpy(to_arr_aux, recv_response, response);
    
    if(-1 == utf8_to_wchar(to_arr_aux, to_arr, response)){
        perror("Error on conversion");
    }
    
    std::wstring ws(to_arr);
    
    std::string str(ws.begin(), ws.end());
    
    rapidjson::Document document;
    
    if(document.Parse<0>(str.c_str()).HasParseError()){
        perror("Internal parsing error");
    }
    
    assert(document.IsObject());

    /*if(document["Error"] != document.Size()){
        perror(std::string(document["Error"].GetString()).c_str());
        //throw PoloException("Error in publishing");
    }*/
    return "OK";
    return document["OK"].GetString();
    
}


int Polo::verify_ip(std::string ip, std::string& reason){
    return 0;
}