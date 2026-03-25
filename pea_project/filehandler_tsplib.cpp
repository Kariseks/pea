#include "filehandler_tsplib.h"
#include <iostream>
#include <fstream>
#include <string>

namespace pea {

Array* FileHandler_TSPLIB::readATSP(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Blad: Nie mozna otworzyc pliku ATSP: " << filename << "\n";
        return nullptr;
    }

    std::string line;
    std::size_t n = 0;

    // Faza 1: Szukanie wymiaru
    while (file >> line) {
        if (line.find("DIMENSION") != std::string::npos) {
            if (line.find(':') != std::string::npos) {
                std::string val = line.substr(line.find(':') + 1);
                if (val.empty()) file >> n;
                else n = std::stoull(val);
            } else {
                file >> line;
                if (line == ":") file >> n;
                else n = std::stoull(line);
            }
            break;
        }
    }

    if (n == 0) {
        std::cerr << "Blad: Nie znaleziono DIMENSION lub wynosi 0.\n";
        return nullptr;
    }

    // Faza 2: Inicjalizacja Twojej klasy
    Array* matrix = new Array(n);

    // Faza 3: Szukanie sekcji wag
    while (file >> line) {
        if (line == "EDGE_WEIGHT_SECTION") break;
    }

    // Faza 4: Wczytywanie danych do macierzy
    int val;
    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t j = 0; j < n; ++j) {
            if (!(file >> val)) {
                std::cerr << "Blad: Za malo danych w sekcji EDGE_WEIGHT_SECTION.\n";
                delete matrix;
                return nullptr;
            }
            matrix->set(val, i, j);
        }
    }

    return matrix;
}

int* FileHandler_TSPLIB::readOptTour(const std::string& filename, int& outN) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Blad: Nie mozna otworzyc pliku z trasa: " << filename << "\n";
        return nullptr;
    }

    std::string line;
    int n = 0;

    // Faza 1: Szukanie wymiaru
    while (file >> line) {
        if (line.find("DIMENSION") != std::string::npos) {
            if (line.find(':') != std::string::npos) {
                std::string val = line.substr(line.find(':') + 1);
                if (val.empty()) file >> n;
                else n = std::stoi(val);
            } else {
                file >> line;
                if (line == ":") file >> n;
                else n = std::stoi(line);
            }
            break;
        }
    }

    if (n <= 0) {
        std::cerr << "Blad: Nieprawidlowy wymiar w pliku trasy.\n";
        return nullptr;
    }

    outN = n;
    int* tour = new int[n];

    // Faza 2: Szukanie sekcji trasy
    while (file >> line) {
        if (line == "TOUR_SECTION") break;
    }

    // Faza 3: Wczytywanie trasy z korektą indeksów (TSPLIB podaje miasta od 1)
    int city;
    for (int i = 0; i < n; ++i) {
        file >> city;
        if (city == -1) {
            std::cerr << "Blad: Przedwczesny koniec trasy.\n";
            delete[] tour;
            return nullptr;
        }
        tour[i] = city - 1; // Zmiana z zakresu 1..N na 0..N-1
    }

    return tour;
}

bool FileHandler_TSPLIB::writeOptTour(const std::string& filename, const int* tour, int n, long long cost) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Blad: Nie mozna utworzyc pliku: " << filename << "\n";
        return false;
    }

    file << "NAME : " << filename << "\n";
    file << "TYPE : TOUR\n";
    file << "DIMENSION : " << n << "\n";
    file << "COMMENT : OPTIMAL_COST = " << cost << "\n";
    file << "TOUR_SECTION\n";

    for (int i = 0; i < n; ++i) {
        // Konwersja indeksu 0..N-1 z powrotem na 1..N dla zachowania standardu TSPLIB
        file << tour[i] + 1 << "\n";
    }

    file << "-1\n";
    file << "EOF\n";

    return true;
}

} // end of namespace pea
