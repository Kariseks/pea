#include "node.h"
#include <cstring>



Node::Node(uint8_t city, uint8_t level, uint8_t parent_path[], uint32_t visited_cities, const int matrix [32][32], int LB)
:
    current_city{city},
    level{level},
    LB(LB),
    visited_cities{visited_cities}
{
    std::memcpy(this->matrix, matrix, sizeof(this->matrix));

    std::memcpy(this->path, parent_path, sizeof(path));
    this->path[level-1] = city; //dodanie aktualnego noda do sciezki
    this->visited_cities |= (1 << current_city);   //miasto jest juz znane

}

