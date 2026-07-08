cmake_minimum_required(VERSION 3.25)

project(SUT LANGUAGES CXX)

add_library(SUT SHARED
        count_matches.cpp
        fibonacci.cpp
        format_list.cpp
        free_functions.cpp
        repeated_sort.cpp
        sut_common.cpp
        top_words_from_file.cpp
)

target_compile_features(SUT PRIVATE cxx_std_23)

target_include_directories(SUT PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
)
