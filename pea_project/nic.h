#ifndef NIC_H
#define NIC_H

#include <stop_token>
#include "array.h"
#include "Result.h"

using namespace pea;
// Pomocnicza funkcja do odwracania fragmentu Twojego Wektora (potrzebna do permutacji)
void tsp_brute_force(std::stop_token stoken, const Array& matrix, Result& out_result);
void tsp_random(std::stop_token stoken, const Array& matrix, Result& out_result);
void tsp_nn(std::stop_token stoken, const Array& matrix, Result& out_result);
void tsp_rnn(std::stop_token stoken, const Array& matrix, Result& out_result);
T calculateTourCost(Wektor& path, const Array & matrix);
bool verifyVisited(Wektor& path);
#endif // NIC_H
