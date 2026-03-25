cmake_minimum_required(VERSION 3.16)

project(pea_project LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(pea_project main.cpp
    array.h array.cpp
    filehandler_tsplib.h filehandler_tsplib.cpp)

include(GNUInstallDirs)
install(TARGETS pea_project
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
