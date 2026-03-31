#ifndef FILEHANDLER_TSPLIB_H
#define FILEHANDLER_TSPLIB_H

#include <string>
#include "Result.h"
#include "array.h" // Plik z Twoją klasą Array

namespace pea {

class FileHandler_TSPLIB {
public:
    // Wczytuje plik .atsp i zwraca zaalokowany obiekt Array.
    // Zwraca nullptr w przypadku błędu.
    static Array * readATSP(const std::string& filename);

    // Wczytuje plik .opt.tour.
    // Zwraca zaalokowaną tablicę int z trasą (indeksowaną od 0),
    // a jej rozmiar zapisuje do zmiennej przekazanej przez referencję.
    static int* readOptTour(const std::string& filename, int& outN);
    static bool readOptTour(const std::string& filename, Result& out_result);
    static bool readOptTourSequence(const std::string& filename, Wektor& out_path);

    // Zapisuje trasę i koszt do pliku .opt.tour.
    // Trasa w tablicy musi być indeksowana od 0 (metoda doda 1 dla standardu TSPLIB).
    static bool writeOptTour(const std::string& filename, const int* tour, int n, long long cost);

    void saveResult(const std::string& algoName, std::size_t size, double cpuTime, const Result& result, int how_optimal) const;
    bool saveResult(const std::string& algoName, std::size_t size, double cpuTime, const Result& result) const;
};

} // end of namespace pea

#endif // FILEHANDLER_TSPLIB_H
