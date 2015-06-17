#ifndef __HPP_CONVERT
#define __HPP_CONVERT

#include <iconv.h>
#include <wchar.h>
#include <stdint.h>

int wchar_to_utf8(wchar_t* input, char* output, size_t output_len){

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

int utf8_to_wchar(char* input, wchar_t* output, size_t output_len){
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

uint32_t parseIPV4string(const char* ipAddress) {
  char ipbytes[4];
  sscanf(ipAddress, "%d.%d.%d.%d", &ipbytes[3], &ipbytes[2], &ipbytes[1], &ipbytes[0]);
  return ipbytes[0] | ipbytes[1] << 8 | ipbytes[2] << 16 | ipbytes[3] << 24;
}

#endif