#ifndef LIBRUNNER_FORMAT_LIST_TESTS_H
#define LIBRUNNER_FORMAT_LIST_TESTS_H

#include <cstddef>

using FormatListFunction = char* (*)(const int*, std::size_t);
using FreeStringFunction = void (*)(char*);

bool run_format_list_tests(
    FormatListFunction format_list,
    FreeStringFunction free_string
);

#endif // LIBRUNNER_FORMAT_LIST_TESTS_H
