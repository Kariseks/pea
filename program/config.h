#ifndef CONFIG_H
#define CONFIG_H


#include <cstdint>

namespace pea{

    using T = int;

    namespace BB
    {
        constexpr uint8_t MAX_N =50;
        constexpr uint8_t MATRIX_COL =64;//musi byc potega 2, zeby indeks wyliczac przsunieciem bitowy
        constexpr int INF = 1'000'000'000; //nie moze byz z limits bo bedziemy dodawac


    }
}


#endif // CONFIG_H
