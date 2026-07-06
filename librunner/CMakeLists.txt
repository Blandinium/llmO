cmake_minimum_required(VERSION 3.25)

project(librunner LANGUAGES CXX)

add_executable(librunner
    count_matches_tests.cpp
    fibonacci_tests.cpp
    format_list_tests.cpp
    main.cpp
    repeated_sort_tests.cpp
    top_words_from_file_tests.cpp
        benchmarks.cpp
        benchmarks.h
        sut_api.h
)

target_compile_features(librunner PRIVATE cxx_std_23)

add_dependencies(librunner SUT)

target_include_directories(librunner PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../SUT
)

target_compile_options(librunner PRIVATE
    -Wall
    -Wextra
    -Wpedantic
)

# Needed for dlopen/dlsym on Linux.
target_link_libraries(librunner PRIVATE
    ${CMAKE_DL_LIBS}
)
