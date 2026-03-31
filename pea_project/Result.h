#ifndef RESULT_H
#define RESULT_H

#include "wektor.h"
#include <limits>

using T = int;
struct Result{
    Wektor path;
    T cost;

    Result() : path(0), cost(std::numeric_limits<int>::max()) {}
};

#endif // RESULT_H
