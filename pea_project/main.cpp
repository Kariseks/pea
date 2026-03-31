#include <filesystem>
#include <iostream>
#include "algorithmrunner.h"
#include "array.h"
#include "filehandler_tsplib.h"
#include "parser.h"
#include "nic.h"
using namespace std;

//=====================================================================================================================
int howOptimal(std::string opt_tour_path, const Result & result, const Array & matrix)
{
    bool successfull;
    Wektor path{1};
    successfull = FileHandler_TSPLIB::readOptTourSequence(opt_tour_path, path);

    if(successfull)
    {
        auto opt_cost = calculateTourCost(path, matrix);
        return ((100.0*opt_cost) / result.cost);
    }
    else
        return 0;

}
//=====================================================================================================================
bool verifyOptimum(std::string opt_tour_path, const Result & result)
{
    bool successfull;
    Wektor path{1};
    successfull = FileHandler_TSPLIB::readOptTourSequence(opt_tour_path, path);
    if(successfull)
        return result.path == path;

    return false;   //couldn't read file
}
bool verifyVisited(const Result & result)
{
    bool successfull;
    Wektor path{1};

    return result.path == path;
}
//=====================================================================================================================
int main(int argc, char ** argv)
{
    //----- parsowanie  ---------------
    Parser parser;
    auto isParsed = parser.parse(argc, argv);
    if (!isParsed){
        cout << "Blad parsowania" << endl;
        return 1;
    }

    auto algoId  = parser.getAlgorithmId();
    auto filePath  = parser.getFilePath();
    auto maxTime  = parser.getMaxTime();
    auto mode = parser.getMode();
    auto algorithm = (algoId == 1) ? tsp_brute_force:
                         (algoId == 2) ? tsp_random :
                         (algoId == 3) ? tsp_nn :
                        (algoId == 4) ? tsp_rnn :
                                tsp_brute_force;

    auto algoName = (algoId == 1) ? "brute_force":
                        (algoId == 2) ? "random" :
                        (algoId == 3) ? "nn" :
                        (algoId == 4) ? "rnn" :
                         "brute_force";
    //---- wczytywanie macierzy z pliku -----------------


    pea::FileHandler_TSPLIB fileHandler;
    auto data = fileHandler.readATSP(filePath);
    if(data == nullptr)
    {
        cout << "Nie wczytano macierzy koniec programu" << endl;
        return 1;
    }


    auto array = Array{std::move(*data)};
    Result result;

    AlgorithmRunner runner;
    bool completed_on_time = false;

    runner.run_with_wall_timeout(std::chrono::minutes(maxTime), algorithm,array, result);
    //--------------------------------------------------------------------------
    //koniec czesci wyznaczania optymalnej trasy i kosztu
    //----- dopisanie/zapis wynikow testu do piku-----------------------------------------------------------------------------
    fileHandler.saveResult(algoName, array.getSize(), runner.getFinal_cpu_time_in_s(), result);
    return 0;

    //----- zapis optymalnej scizeki i kosztu do pliku ----------------------------------------------------------------
    std::filesystem::path path_tmp(filePath);
    auto outFileName = path_tmp.stem().string()+"_" + algoName + ".opt.tour";

    //----- -----------------------------------------------


    auto opt_tour_path = std::to_string(array.getSize()) + ".opt.tour";
    auto how_optimal = howOptimal(opt_tour_path, result, array);

    if(mode)
    {
        Wektor path{1};
        auto successfull = FileHandler_TSPLIB::readOptTourSequence(opt_tour_path, path);
        if(!successfull)
            cout << "" << endl;
         auto is_verified = verifyOptimum(opt_tour_path, result);
        string output_res = "nieprawidlowy";
        if(is_verified)
            output_res = "prawidlowy";
        cout << algoName << " dla rozmiaru " << array.getSize() << " jest " << output_res << endl;
    }
    cout << "Koszt: " << result.cost << endl;
    cout << "Czas: " << runner.getFinal_cpu_time_in_s() << " sekund" << endl;
    cout << result.path << endl;

}
