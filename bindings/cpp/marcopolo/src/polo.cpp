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

#define PORT 1390
#define ADDRESS "127.0.0.1"

Polo::Polo(){
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
    

    SSL_write(ssl, "Hola", sizeof("Hola"));
    char buf_recv[500];
    SSL_read(ssl, buf_recv, 500);

    this->wrappedSocket = ssl;
    
    printf("%s\n", buf_recv);
}

Polo::~Polo(){

}