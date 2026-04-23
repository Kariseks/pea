#ifndef ETAP_1_H
#define ETAP_1_H

#include <stop_token>
#include "array.h"
#include "Result.h"

using namespace pea;
// Pomocnicza funkcja do odwracania fragmentu Twojego Wektora (potrzebna do permutacji)
Result tsp_brute_force(const Array& matrix);
Result tsp_random(std::stop_token stoken, const Array& matrix);
Result tsp_nn(const Array& matrix);
Result tsp_rnn(const Array& matrix);
T calculateTourCost(const Wektor& path, const Array & matrix);
bool verifyVisited(Wektor& path);
void tsp_random_iter(std::size_t count, const Array& matrix, Result& out_result);

#endif // ETAP_1_H
