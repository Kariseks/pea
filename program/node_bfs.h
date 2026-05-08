#ifndef NODE_BFS_H
#define NODE_BFS_H


#include <cstdint>

#include "config.h"

struct NodeBFS {

    int matrix[pea::BB::MAX_N][pea::BB::MATRIX_COL];
    int LB = 0;
    uint8_t level = 0;
    uint8_t path[pea::BB::MAX_N];
    uint8_t current_city = 0;
    uint64_t visited_cities = 0;

    // Konstruktor
    NodeBFS(uint8_t city, uint8_t level, uint8_t parent_path[], uint64_t visited_cities, const int matrix [][pea::BB::MATRIX_COL], int LB);
    NodeBFS() = delete;
    NodeBFS(NodeBFS&&) = default;
    NodeBFS(const NodeBFS&) = default; //kopiowanie w struktruahc

};




#endif // NODE_BFS_H
