#ifndef NODE_H
#define NODE_H

#include "array.h"
#include "wektor.h"
#include <utility>

struct Node {
    pea::Array reduceMatrix;
    Wektor path;
    bool* visited;
    T cost;
    T bound;
    int level;

    Node(int n) : reduceMatrix(n), path(n) {
        visited = new bool[n]{false};
        cost = 0;
        bound = 0;
        level = 0;
    }

    // Konstruktor kopiujący
    Node(const Node& other) : reduceMatrix(other.reduceMatrix), path(other.path) {
        int n = reduceMatrix.getSize();
        visited = new bool[n];
        for (int i = 0; i < n; i++) {
            visited[i] = other.visited[i];
        }
        cost = other.cost;
        bound = other.bound;
        level = other.level;
    }

    // Konstruktor przenoszący (KLUCZOWY dla wydajności przy std::stack)
    Node(Node&& other) noexcept
        : reduceMatrix(std::move(other.reduceMatrix)),
        path(std::move(other.path)),
        visited(std::exchange(other.visited, nullptr)),
        cost(other.cost),
        bound(other.bound),
        level(other.level) {}

    ~Node() {
        delete[] visited;
    }
};


#endif // NODE_H
