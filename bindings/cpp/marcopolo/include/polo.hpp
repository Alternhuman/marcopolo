#ifndef _POLO_HPP
#define _POLO_HPP

#include <string>
#include <vector>
#include <exception>
#include <openssl/ssl.h>

#include "service.hpp"


#define INVALID_NAME_SERVICE 1

/*class PoloException: public exception
{
  virtual const char* what() const throw()
  {
    return "My exception happened";
  }
} PoloException;*/

class Polo{
public:
    Polo();
    ~Polo();
    
    /*std::string publish_service(std::string service, std::vector<std::string> multicast_groups, bool permanent=false, bool root=false);
    int unpublish_service(std::string service, std::vector<std::string> multicast_groups, bool delete_file=false);
    Service service_info(std::string service);
    bool has_service(service);

    int set_permanent(std::string service, bool permanent=true);

    int reload_services();*/

private:
    int polo_socket;
    SSL *wrappedSocket;
    /*get_token();
    request_token();
    verify_parameters(std::string service, std::vector<std::string> multicast_groups)*/
};

#endif