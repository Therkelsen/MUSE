cmake_minimum_required(VERSION 3.20)
project(MUSE VERSION 0.1.0 LANGUAGES C CXX)

include(CTest)
enable_testing()

project(MUSE)
set(CMAKE_CXX_STANDARD 20)
add_executable(MUSE sources/main.cpp sources/DataInterface.cpp headers/DataInterface.h)

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)