#ifndef __HPP_CONVERT
#define __HPP_CONVERT

#include <iconv.h>
#include <wchar.h>

int wchar_to_utf8(wchar_t* input, char* output, size_t output_len);
int utf8_to_wchar(char* input, wchar_t* output, size_t output_len);

#endif