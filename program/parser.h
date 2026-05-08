#ifndef PARSER_H
#define PARSER_H

#include <string>
#include <sstream>

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
    std::string getError() const;
    //int getMode() const;
private:
    static constexpr int arg_num = 3;
    std::stringstream errorMsg;
};

#endif // PARSER_H
