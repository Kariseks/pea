#include "etap_2.h"
#include "etap_1.h"

using namespace std;
using namespace pea;

namespace
{

}



Result bredth_first_search(const Array &matrix)
{
    auto ub_res = tsp_rnn(matrix);
}

Result deep_first_search(const pea::Array & matrix)
{
    //#1 wyznaczenie UB, żeby juz w pierwszym przebiegu wycinać nie rokujące ścieżki
    auto ub_res = tsp_rnn(matrix);

    //#2 Stowrzenie koleji LIFO na Node


    //#2 Inicjalizacja root Node,


        // Konstruktor
        Node(int8_t current_city, int8_t level, int8_t path[], int32_t unknown_cities, const pea::Array & matrix);




}
Result best_first_search(const pea::Array & matrix)
{

}
