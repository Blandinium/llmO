#ifndef SUT_COMMON_H
#define SUT_COMMON_H

#include <string>

char* copy_to_c_string(const std::string& value);
bool is_word_char(char c);
char normalize_char(char c);

#endif // SUT_COMMON_H
