#ifndef _POLO_HPP
#define _POLO_HPP

#include <stdio.h>

#include <string>
#include <vector>
#include <exception>
#include <openssl/ssl.h>

#include "service.hpp"
#include "convert.hpp"


#define INVALID_NAME_SERVICE 1

class PoloException: public std::exception
{
public:
  PoloException(std::string msg){
    this->msg = msg;
  }
  ~PoloException() throw(){}
  virtual const char* what() const throw()
  {
    return this->msg.c_str();
  }
private:
    std::string msg;
};

class Polo{
public:
    Polo(int timeout=0);
    ~Polo();
    
    std::string publish_service(std::string service, std::vector<std::string> multicast_groups=std::vector<std::string>(), bool permanent=false, bool root=false);
    int unpublish_service(std::string service, std::vector<std::string> multicast_groups=std::vector<std::string>(), bool delete_file=false);
    /*Service service_info(std::string service);
    bool has_service(service);

    int set_permanent(std::string service, bool permanent=true);

    int reload_services();*/

private:
    int polo_socket;
    SSL *wrappedSocket;
    std::string get_token();
    std::string request_token(const struct passwd*);
    int verify_ip(std::string, std::string&);
    int verify_common_parameters(const std::string service, const std::vector<std::string> multicast_groups, std::string &reason);
    
    /*verify_parameters(std::string service, std::vector<std::string> multicast_groups)*/
};

#endif