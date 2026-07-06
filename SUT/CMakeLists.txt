cmake_minimum_required(VERSION 3.25)

project(SUT LANGUAGES CXX)

add_library(SUT SHARED
        library.cpp
)

target_compile_features(SUT PRIVATE cxx_std_23)

target_include_directories(SUT PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
)