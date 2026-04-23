#ifndef NODE_H
#define NODE_H


#include <cstdint>

const int INF = 100000000; // Bezpieczna nieskończoność (nie wywali overflow przy dodawaniu)

struct Node {
    int matrix[32][32];
    int LB = 0;
    uint8_t level = 0;
    uint8_t path[32];
    uint8_t current_city = 0;
    uint32_t visited_cities = 0;

    // Konstruktor
    Node(uint8_t city, uint8_t level, uint8_t parent_path[], uint32_t visited_cities, const int matrix [32][32], int LB);
    Node() = delete;
    Node(Node&&) = default;

};




#endif // NODE_H
