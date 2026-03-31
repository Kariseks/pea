#ifndef PARSER_H
#define PARSER_H

#include <string>

class Parser {
private:
    int maxTime;
    int algorithmId;
    std::string filePath;
    bool valid;
    int mode;

public:
    Parser();

    // Główna funkcja parsująca. Zwraca true jeśli argumenty są poprawne.
    bool parse(int argc, char* argv[]);

    // Gettery
    int getMaxTime() const;
    int getAlgorithmId() const;
    std::string getFilePath() const;
    bool isValid() const;
    int getMode() const;
};

#endif // PARSER_H
