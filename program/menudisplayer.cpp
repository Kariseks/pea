#include "menudisplayer.h"

#include <iostream>


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

    while(true) //nieskonczona petla sprawdzania algorytmu, na wybranym pliku
    {
        //#2 ===== Wybor algorytmu =====
        cout << "Wybierz algorytm (podaj liczbę całkowitą): "<<endl
             << "\t0-zakoncz program" << endl
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
        if(algoId == 0)
            return 0;   //wybrano zakonczenie programu

        auto algorithm = (algoId == 1) ? tsp_brute_force:
                             (algoId == 2) ? tsp_brute_force :
                             (algoId == 3) ? tsp_nn :
                             (algoId == 4) ? tsp_rnn :
                             (algoId == 5) ? breadth_first_search :
                             (algoId == 6) ? deep_first_search :
                             (algoId == 7) ? best_first_search :
                             tsp_brute_force;
        int maxTime;
        if(algoId == 2)
        {
            cout << "Wpisz ograniczenie czasowe algorytmu w sekundach\n\tmaks czas:= ";
            cin >> maxTime;
            cout << endl;
        }


        //#3 Uruchomienie runnera
        auto array = Array{*data};  //kopiowanie zeby mozna bylo wiele przebiegow petli
        Result result;
        AlgorithmRunner runner;
        runner.run(algorithm, array);
        result = runner.getResult();

        //#4. Wypisanie wyniku obliczen
        cout << result.path << endl;
        cout << "Koszt: " << result.cost << endl;
        cout << "Czas: " << runner.getFinal_cpu_time_in_s() << " sekund" << endl;
        cout << string(50,'-') << endl;
    }
}
