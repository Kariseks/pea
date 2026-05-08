#include <filesystem>
#include <iostream>
#include "algorithmrunner.h"
#include "array.h"
#include "etap_2.h"
#include "filehandler_tsplib.h"
#include "menudisplayer.h"
#include "parser.h"
#include "etap_1.h"
using namespace std;


//=====================================================================================================================
/* ARGUMENTY
 * <time in minutes><algo id><file_path><mode>
 *
 *
 */
//=====================================================================================================================
int main(int argc, char ** argv)
{
    if(argc == 1)   //wywolanie bez arguemntow -> tryb z menu
    {
        displayMenu(argc, argv);
    }
    else    //wywolanie z argumentmai ->
    {

        //----- parsowanie  ---------------
        Parser parser;
        auto isParsed = parser.parse(argc, argv);
        if (!isParsed){
            cout << parser.getError() << endl;
            return 1;
        }

        auto algoId  = parser.getAlgorithmId();
        auto filePath  = parser.getFilePath();
        auto maxTime  = parser.getMaxTime();
        auto algorithm = (algoId == 1) ? tsp_brute_force:
                             (algoId == 2) ? tsp_brute_force :
                             (algoId == 3) ? tsp_nn :
                             (algoId == 4) ? tsp_rnn :
                             (algoId == 5) ? breadth_first_search :
                             (algoId == 6) ? deep_first_search :
                             (algoId == 7) ? best_first_search :
                             tsp_brute_force;

        auto algoName = (algoId == 1) ? "brute_force":
                            (algoId == 2) ? "random" :
                            (algoId == 3) ? "nn" :
                            (algoId == 4) ? "rnn" :
                            (algoId == 5) ? "breadth_first_search" :
                            (algoId == 6) ? "deep_first_search" :
                            (algoId == 7) ? "best_first_search" :
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
        if(algoId == 2)
            runner.run_iterations(maxTime,tsp_random_iter,array, result);
        else{
            runner.run(algorithm,array);
            result =runner.getResult();
        }

        //--------------------------------------------------------------------------
        //koniec czesci wyznaczania optymalnej trasy i kosztu
        //----- dopisanie/zapis wynikow testu do piku-----------------------------------------------------------------------------
        std::filesystem::path res_path_tmp(filePath);
        auto resFileName = res_path_tmp.stem().string()+"_wyniki.csv";
        //fileHandler.saveResult(algoName, resFileName, array.getSize(), runner.getFinal_cpu_time_in_s(), result);
        std::filesystem::path pathObj(filePath);
        fileHandler.saveResult(pathObj.stem().string(),algoName, "wyniki.csv", array.getSize(), runner.getFinal_cpu_time_in_s(), result);
    }
}

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