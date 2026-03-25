#include <iostream>

using namespace std;

int main()
{
    cout << "Hello World!" << endl;
    return 0;
}
/*
// ==================== PRZYKŁAD UŻYCIA ====================

int main() {
    AlgorithmRunner runner;

    // Zmienne, w których chcemy zapisać wyniki (poza klasą Runner)
    long long znaleziony_wynik = 0;
    bool czy_skonczyl_cale_zadanie = false;

    // Definiujemy nasz algorytm jako lambdę.
    // [&] oznacza: daj lambdzie dostęp przez referencję do wszystkich zmiennych powyżej (wyników).
    auto moj_ciezki_algorytm = [&](const std::atomic<bool>& timeout_flag) {
        std::cout << "[Algorytm] Zaczynam obliczenia...\n";

        for (long long i = 0; i < 50'000'000'000; ++i) {

            // Kooperatywne sprawdzanie flagi co 10 000 iteracji
            if (i % 10'000 == 0 && timeout_flag.load(std::memory_order_relaxed)) {
                std::cout << "[Algorytm] Ups, czas minal. Sprzatam po sobie i koncze.\n";
                czy_skonczyl_cale_zadanie = false;
                return; // Wychodzimy z lambdy
            }

            // ... symulacja ciężkiej pracy ...
            znaleziony_wynik += 1;
        }

        czy_skonczyl_cale_zadanie = true;
        std::cout << "[Algorytm] Skonczylem naturalnie!\n";
    };

    std::cout << "--- TEST 1: Zbyt krotki czas (1 sekunda) ---\n";
    // Odpalamy algorytm z limitem 1 sekundy
    runner.run_with_timeout(moj_ciezki_algorytm, std::chrono::seconds(1));

    // Zobacz, wyniki są bezpiecznie zaktualizowane w main!
    std::cout << "Wyniki w main -> Czy udalo sie w calosci? "
              << (czy_skonczyl_cale_zadanie ? "TAK" : "NIE")
              << " | Naliczono: " << znaleziony_wynik << "\n\n";

    return 0;
}
*/
