cmake_minimum_required(VERSION 3.16)

project(pea_project LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(pea_project main.cpp
    array.h array.cpp
    filehandler_tsplib.h filehandler_tsplib.cpp
    algorithmrunner.h algorithmrunner.cpp
    Result.h
    wektor.h wektor.cpp
    parser.h parser.cpp
    etap_1.h etap_1.cpp
    etap_2.h etap_2.cpp
    menudisplayer.h menudisplayer.cpp
    doublelista.h doublelista.cpp
    node_bfs.h node_bfs.cpp
    config.h
    stack.h stack.cpp
    node.h node.cpp
    nodestack.h nodestack.cpp
    nodequeue.h nodequeue.cpp
    nodepriorityqueue.h nodepriorityqueue.cpp)

include(GNUInstallDirs)
install(TARGETS pea_project
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
