cmake_minimum_required(VERSION 3.17)

project(wands_server)

set(CMAKE_CXX_STANDARD 17)

find_package(HDF5 REQUIRED COMPONENTS CXX HL)
find_package(Boost REQUIRED COMPONENTS program_options)
find_package(ADIOS2 REQUIRED)
find_package(Threads REQUIRED)

add_executable(wands_server main.cpp)
target_link_libraries(wands_server PRIVATE HDF5::HDF5 Boost::boost Boost::program_options adios2::cxx11 Threads::Threads)

# add_executable(wands_server_group server_group/main.cpp)
# target_link_libraries(wands_server_group PRIVATE HDF5::HDF5 Boost::boost adios2::cxx11 Threads::Threads)

add_executable(test_client test_client.cpp)
target_link_libraries(test_client PRIVATE adios2::cxx11)
