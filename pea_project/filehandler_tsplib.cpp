#include "filehandler_tsplib.h"
#include <iostream>
#include <fstream>
#include <string>
#include <ctime>
#include <iomanip>

namespace pea {
using namespace std;

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

bool FileHandler_TSPLIB::readOptTour(const std::string& filename, Result& out_result) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Blad: Nie mozna otworzyc pliku: " << filename << "\n";
        return false;
    }

    std::string line;
    int n = 0;
    out_result.cost = 0; // Domyślnie 0, jeśli nie znajdziemy COMMENT
    bool tourSectionFound = false;

    // Faza 1: Czytanie nagłówka linia po linii
    while (std::getline(file, line)) {
        // Szukanie DIMENSION
        if (line.find("DIMENSION") != std::string::npos) {
            size_t pos = line.find(':');
            if (pos != std::string::npos) {
                n = std::stoi(line.substr(pos + 1));
            } else {
                // Obsługa przypadku "DIMENSION 17" bez dwukropka
                std::stringstream ss(line);
                std::string tmp;
                ss >> tmp >> n;
            }
        }

        // Szukanie kosztu w COMMENT
        if (line.find("COMMENT") != std::string::npos) {
            // Szukamy liczby po znaku '=' lub po słowie 'is'
            size_t pos = line.find_last_of("= ");
            if (pos != std::string::npos) {
                try {
                    out_result.cost = std::stoi(line.substr(pos + 1));
                } catch (...) {
                    out_result.cost = 0; // W razie błędu parsowania
                }
            }
        }

        // Sprawdzenie czy doszliśmy do sekcji trasy
        if (line.find("TOUR_SECTION") != std::string::npos) {
            tourSectionFound = true;
            break;
        }

        if (line.find("EOF") != std::string::npos) break;
    }

    // Faza 2: Obsługa trasy
    if (tourSectionFound && n > 0) {
        out_result.path = Wektor(n);
        int city;
        for (int i = 0; i < n; ++i) {
            if (!(file >> city) || city == -1) {
                // Jeśli plik nagle się urwał, czyścimy wektor
                out_result.path = Wektor(0);
                break;
            }
            out_result.path[i] = city - 1; // Konwersja 1..N na 0..N-1
        }
    } else {
        // Jeśli nie znaleziono TOUR_SECTION, ustawiamy pusty wektor
        out_result.path = Wektor(0);
    }

    return true;
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

bool FileHandler_TSPLIB::saveResult(const std::string &algoName, std::size_t size, double cpuTime, const Result &result) const
{
    // 1. Dynamiczne tworzenie nazwy pliku: np. BruteForce_12.csv
    std::string filename = algoName + "_" + std::to_string(size) + ".csv";

    // 2. Otwarcie pliku w trybie dopisywania (std::ios::app)
    // Jeśli plik nie istnieje, zostanie utworzony. Jeśli istnieje, nowa linia trafi na koniec.
    std::ofstream file(filename, std::ios::app);

    // Prosta obsługa błędu otwarcia pliku
    if (!file.is_open()) {
        std::cerr << "[Parser] Blad krytyczny: Nie mozna otworzyc pliku " << filename << " do zapisu!\n";
        return false;
    }

    // 3. Pobranie aktualnego czasu systemowego
    std::time_t now = std::time(nullptr);

    // Konwersja na strukturę czasu lokalnego (godziny, minuty, dni...)
    // Uwaga: Jeśli używasz Visual Studio i dostaniesz błąd C4996,
    // dodaj #define _CRT_SECURE_NO_WARNINGS na samej gorze pliku.
    std::tm* now_tm = std::localtime(&now);

    // 4. Zapis do pliku zgodnie z formatem:
    // czas;size;algo_name;data;data_zapisu
    // gdzie 'data' to u Ciebie koszt (result.cost)
    // a 'data_zapisu' to MM:HH DD-MM-RRRR

    file << cpuTime << ";"                   // Kolumna 1: czas (CPU)
         << size << ";"                      // Kolumna 2: rozmiar instancji
         << algoName << ";"                  // Kolumna 3: nazwa algorytmu
         << result.cost << ";"               // Kolumna 4: wynik (koszt)
         << std::put_time(now_tm, "%H:%M %d-%m-%Y") // Kolumna 6: MM:HH DD-MM-RRRR
         << "\n";

    file.close(); // Zamknięcie pliku

    std::cout << "[Parser] Wynik pomiaru dopisany do pliku: " << filename << "\n";
    return true;
}

void FileHandler_TSPLIB::saveResult(const std::string &algoName, std::size_t size, double cpuTime, const Result &result, int how_optimal) const
{
    // 1. Dynamiczne tworzenie nazwy pliku: np. BruteForce_12.csv
    std::string filename = algoName + "_" + std::to_string(size) + ".csv";

// 2. Otwarcie pliku w trybie dopisywania (std::ios::app)
// Jeśli plik nie istnieje, zostanie utworzony. Jeśli istnieje, nowa linia trafi na koniec.
std::ofstream file(filename, std::ios::app);

// Prosta obsługa błędu otwarcia pliku
if (!file.is_open()) {
    std::cerr << "[Parser] Blad krytyczny: Nie mozna otworzyc pliku " << filename << " do zapisu!\n";
    return;
}

// 3. Pobranie aktualnego czasu systemowego
std::time_t now = std::time(nullptr);

// Konwersja na strukturę czasu lokalnego (godziny, minuty, dni...)
// Uwaga: Jeśli używasz Visual Studio i dostaniesz błąd C4996,
// dodaj #define _CRT_SECURE_NO_WARNINGS na samej gorze pliku.
std::tm* now_tm = std::localtime(&now);

// 4. Zapis do pliku zgodnie z formatem:
// czas;size;algo_name;data;data_zapisu
// gdzie 'data' to u Ciebie koszt (result.cost)
// a 'data_zapisu' to MM:HH DD-MM-RRRR

file << cpuTime << ";"                   // Kolumna 1: czas (CPU)
    << size << ";"                      // Kolumna 2: rozmiar instancji
    << algoName << ";"                  // Kolumna 3: nazwa algorytmu
    << result.cost << ";"               // Kolumna 4: wynik (koszt)
     << how_optimal << ";"              // Kolumna 5: % optymalnosci
    << std::put_time(now_tm, "%H:%M %d-%m-%Y") // Kolumna 6: MM:HH DD-MM-RRRR
    << "\n";

file.close(); // Zamknięcie pliku

std::cout << "[Parser] Wynik pomiaru dopisany do pliku: " << filename << "\n";
}





bool FileHandler_TSPLIB::readOptTourSequence(const std::string& filename, Wektor& out_path) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Blad: Nie mozna otworzyc pliku z trasa: " << filename << "\n";
        return false;
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
        return false;
    }

    // Faza 2: Szukanie sekcji trasy
    while (file >> line) {
        if (line == "TOUR_SECTION") break;
    }

    // Faza 3: Inicjalizacja Twojego wektora odpowiednim rozmiarem
    out_path = Wektor(n);

    // Faza 4: Wczytywanie z korektą indeksów z TSPLIB (1..N) na C++ (0..N-1)
    int city;
    for (int i = 0; i < n; ++i) {
        file >> city;
        if (city == -1) {
            std::cerr << "Blad: Przedwczesny koniec trasy w pliku.\n";
            return false;
        }
        // Zamiana indeksu (jeśli w pliku jest miasto nr 1, w C++ to indeks 0)
        out_path[i] = city - 1;
    }

    return true;
}















} // end of namespace pea
