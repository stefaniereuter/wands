cmake_minimum_required(VERSION 3.0)

project(wands_server)

set(CMAKE_CXX_STANDARD 17)

find_package(HDF5 REQUIRED COMPONENTS CXX HL)
find_package(Boost REQUIRED)
find_package(ADIOS2 REQUIRED)

add_executable(wands_server main.cpp)
target_link_libraries(wands_server PRIVATE HDF5::HDF5 Boost::boost adios2::cxx11)

add_executable(test_client test_client.cpp)
target_link_libraries(test_client PRIVATE adios2::cxx11)