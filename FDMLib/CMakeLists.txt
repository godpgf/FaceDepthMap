cmake_minimum_required(VERSION 2.8)
project(FDMLib)

set(CMAKE_CXX_STANDARD 14)

add_definitions(-std=c++11)
add_definitions("-Wall")
add_compile_options(-fPIC)
add_compile_options(-c)
set(BUILD_USE_64BITS on)
add_library(fdm_sttc STATIC libfdm_api.cpp libfdm_api.h)
add_library(fdm_dymc SHARED libfdm_api.cpp libfdm_api.h)