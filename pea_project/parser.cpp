#include "parser.h"

#include <iostream>
#include <string>



//<time in minutes><algo id><file_path><mode>
Parser::Parser()
    : maxTime(0), algorithmId(0), filePath(""), valid(false) {}

bool Parser::parse(int argc, char* argv[]) {
    // Program wymaga dokładnie 3 argumentów (argc == 4, bo argv[0] to nazwa programu)
    if (argc != 5) {
        std::cerr << "Blad: Nieprawidlowa liczba argumentow.\n"
                  << "Uzycie: " << argv[0] << " <max_czas> <id_algorytmu_1-10> <sciezka_do_pliku>\n";
        valid = false;
        return false;
    }

    // Parsowanie argumentu 1: Max czas
    try {
        maxTime = std::stoi(argv[1]);
        if (maxTime <= 0) {
            std::cerr << "Blad: Maksymalny czas musi byc wartoscia dodatnia.\n";
            valid = false;
            return false;
        }
    } catch (...) {
        std::cerr << "Blad: Argument 1 (max czas) musi byc liczba calkowita.\n";
        valid = false;
        return false;
    }

    // Parsowanie argumentu 2: ID od 1 do 10
    try {
        algorithmId = std::stoi(argv[2]);
        if (algorithmId < 1 || algorithmId > 10) {
            std::cerr << "Blad: Argument 2 (id) musi byc w przedziale od 1 do 10.\n";
            valid = false;
            return false;
        }
    } catch (...) {
        std::cerr << "Blad: Argument 2 (id) musi byc liczba calkowita.\n";
        valid = false;
        return false;
    }

    // Parsowanie argumentu 3: Ścieżka (względna)
    filePath = argv[3];
    if (filePath.empty()) {
        std::cerr << "Blad: Sciezka do pliku nie moze byc pusta.\n";
        valid = false;
        return false;
    }

    // Parsowanie argumentu 4: Ścieżka (względna)
    try {
        mode = std::stoi(argv[4]);
        if (mode != 0 && mode != 1) {
            std::cerr << "Blad nieprawidlowy mode, moze byc tylko 0(tryb zwykly) lub 1 (tryb weryfikacji).\n";
            valid = false;
            return false;
        }
    } catch (...) {
        std::cerr << "Blad: Argument 4 (mode) nieprawidlowy format.\n";
        valid = false;
        return false;
    }

    valid = true;
    return true;
}

int Parser::getMaxTime() const { return maxTime; }
int Parser::getAlgorithmId() const { return algorithmId; }
int Parser::getMode() const { return mode; }
std::string Parser::getFilePath() const { return filePath; }
bool Parser::isValid() const { return valid; }


