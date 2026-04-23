#include "menudisplayer.h"

#include <iostream>
#include <filesystem>


#include "algorithmrunner.h"
#include "etap_1.h"
#include "etap_2.h"
#include "filehandler_tsplib.h"

using namespace std;
using namespace pea;

int displayMenu(int argc, char **argv)
{
    //#1 ===== Załadowanie pliku ======
    string filePath;
    cout << "Wskaż ścieżkę do pliku z danymi\n\tścieżka:= ";
    cin >> filePath;
    cout << endl;

    pea::FileHandler_TSPLIB fileHandler;
    auto data = fileHandler.readATSP(filePath);
    if(data == nullptr)
    {
        cout << "Nie wczytano macierzy koniec programu" << endl;
        return 1;
    }

    //#2 ===== Wybor algorytmu =====
    cout << "Wybierz algorytm (podaj liczbę całkowitą): "<<endl
         << "\t1-brute force" << endl
         << "\t2-random"    << endl
         << "\t3-najbliższy sąsiad"  << endl
         << "\t4-najbliższy sąsiad z powtarzaniem" << endl
          << "\t5-B&B Breadth first search" << endl
          << "\t6-B&B Deep first search" << endl
          << "\t7-B&B Best first search" << endl
         << "algoId:= ";
    int algoId;
    cin >> algoId;
    cout << endl;

    auto algorithm = (algoId == 1) ? tsp_brute_force:
                         (algoId == 2) ? tsp_brute_force :
                         (algoId == 3) ? tsp_nn :
                         (algoId == 4) ? tsp_rnn :
                         (algoId == 5) ? bredth_first_search :
                         (algoId == 6) ? deep_first_search :
                         (algoId == 7) ? best_first_search :
                         tsp_brute_force;
    auto algoName = (algoId == 1) ? "brute_force":
                        (algoId == 2) ? "random" :
                        (algoId == 3) ? "nn" :
                        (algoId == 4) ? "rnn" :
                        (algoId == 5) ? "breadth" :
                        (algoId == 6) ? "deep" :
                        (algoId == 7) ? "best" :
                        "brute_force";
    int maxTime;
    if(algoId == 2)
    {
        cout << "Wpisz ograniczenie czasowe algorytmu w sekundach\n\tmaks czas:= ";
        cin >> maxTime;
        cout << endl;
    }


    //#3 Uruchomienie runnera
    auto array = Array{std::move(*data)};
    Result result;
    AlgorithmRunner runner;
    runner.run(algorithm, array);
    result = runner.getResult();
    //--------------------------------------------------------------------------
    //koniec czesci wyznaczania optymalnej trasy i kosztu
    //----- dopisanie/zapis wynikow testu do piku-----------------------------------------------------------------------------
    std::filesystem::path res_path_tmp(filePath);
    auto resFileName = res_path_tmp.stem().string()+"_wyniki.csv";
    //fileHandler.saveResult(algoName, resFileName, array.getSize(), runner.getFinal_cpu_time_in_s(), result);
    fileHandler.saveResult(algoName, "wyniki.csv", array.getSize(), runner.getFinal_cpu_time_in_s(), result);

    /*
    //----- zapis optymalnej scizeki i kosztu do pliku ----------------------------------------------------------------
    std::filesystem::path path_tmp(filePath);
    auto outFileName = path_tmp.stem().string()+"_" + algoName + ".opt.tour";
    //----- -----------------------------------------------

    auto opt_tour_path = std::to_string(array.getSize()) + ".opt.tour";
    auto how_optimal = howOptimal(opt_tour_path, result, array);
    */

    cout << "Koszt: " << result.cost << endl;
    cout << "Czas: " << runner.getFinal_cpu_time_in_s() << " sekund" << endl;
    cout << result.path << endl;
}
