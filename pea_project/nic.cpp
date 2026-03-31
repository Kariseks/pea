#include "nic.h"
#include <random>


using namespace pea;

void tsp_nn_wew(std::stop_token stoken, const Array& matrix, Result& out_result, int start);

// Pomocnicza funkcja do odwracania fragmentu Twojego Wektora (potrzebna do permutacji)
void odworoc_wektor(Wektor& w, std::size_t start, std::size_t end) {
    while (start < end) {
        std::swap(w[start], w[end]);
        start++;
        end--;
    }
}

// Ręczna implementacja next_permutation
bool nastepna_permutacja(Wektor& w, std::size_t n) {
    if (n <= 2) return false; // Bo indeks 0 jest zamrożony, więc permutujemy od indeksu 1

    std::size_t i = n - 2;
    // Szukamy pierwszego elementu od prawej mniejszego od swojego następnika
    while (i > 0 && w[i] >= w[i + 1]) {
        i--;
    }

    if (i == 0) return false; // Wszystkie permutacje sprawdzone

    std::size_t j = n - 1;
    // Szukamy elementu większego od w[i]
    while (w[j] <= w[i]) {
        j--;
    }

    std::swap(w[i], w[j]);
    odworoc_wektor(w, i + 1, n - 1);
    return true;
}

void tsp_brute_force(std::stop_token stoken, const Array& matrix, Result& out_result) {
    // Uzyskujemy rozmiar z Twojej klasy Array
    std::size_t n = const_cast<Array&>(matrix).getSize();

    if (n < 2) return;

    // 1. Przygotowanie ścieżki za pomocą Twojego Wektora
    // Używamy konstruktora z rozmiarem
    Wektor current_path(n);
    for (std::size_t i = 0; i < n; ++i) {
        current_path[i] = static_cast<int>(i);
    }

    out_result.cost = std::numeric_limits<int>::max();

    // 2. Główna pętla Brute Force
    do {
        // --- SPRAWDZENIE TIMEOUTU ---
        if (stoken.stop_requested()) {
            return;
        }

        // 3. Obliczanie kosztu bieżącej ścieżki
        T current_cost = 0;

        // Iterujemy po macierzy Array
        for (std::size_t i = 0; i < n - 1; ++i) {
            current_cost += matrix.get(current_path[i], current_path[i+1]);
        }
        // Powrót do początku
        current_cost += matrix.get(current_path[n-1], current_path[0]);

        // 4. Aktualizacja najlepszego wyniku
        if (current_cost < out_result.cost) {
            out_result.cost = current_cost;

            // Kopiujemy ścieżkę do out_result.path
            // Ponieważ Twoje klasy mają operatory przypisania (=), możemy po prostu skopiować obiekt
            out_result.path = current_path;
        }

    } while (nastepna_permutacja(current_path, n));
}
//=====================================================================================================================
void tsp_random(std::stop_token stoken, const Array& matrix, Result& out_result) {
    // Uzyskujemy rozmiar z Twojej klasy Array
    std::size_t n = const_cast<Array&>(matrix).getSize();

    if (n < 2) return;

    // 1. Przygotowanie początkowej ścieżki
    Wektor current_path(n);
    for (std::size_t i = 0; i < n; ++i) {
        current_path[i] = static_cast<int>(i);
    }

    out_result.cost = std::numeric_limits<int>::max();

    // Inicjalizacja profesjonalnego generatora liczb losowych (Mersenne Twister)
    std::random_device rd;
    std::mt19937 rng(rd());

    // 2. Główna pętla algorytmu losowego (działa w nieskończoność aż do timeoutu)
    while (true) {
        // --- SPRAWDZENIE TIMEOUTU ---
        if (stoken.stop_requested()) {
            return;
        }

        // 3. Losowe przetasowanie miast (Algorytm Fishera-Yatesa)
        // Podobnie jak w BF, miasto na indeksie 0 zostawiamy w spokoju (nie ruszamy go),
        // tasujemy tylko miasta od indeksu 1 do n-1.
        for (std::size_t i = n - 1; i > 1; --i) {
            std::uniform_int_distribution<std::size_t> dist(1, i);
            std::size_t j = dist(rng);
            std::swap(current_path[i], current_path[j]);
        }

        // 4. Obliczanie kosztu wylosowanej ścieżki
        T current_cost = 0;

        for (std::size_t i = 0; i < n - 1; ++i) {
            current_cost += const_cast<Array&>(matrix).get(current_path[i], current_path[i+1]);
        }
        // Powrót do początku
        current_cost += const_cast<Array&>(matrix).get(current_path[n-1], current_path[0]);

        // 5. Aktualizacja najlepszego wyniku
        if (current_cost < out_result.cost) {
            out_result.cost = current_cost;

            // Kopiujemy najlepszą znalezioną do tej pory losową ścieżkę
            out_result.path = current_path;
        }
    }
}
//=====================================================================================================================
void tsp_nn(std::stop_token stoken, const Array& matrix, Result& out_result) {
    tsp_nn_wew(stoken,matrix,out_result, 0);
}
//=====================================================================================================================
void tsp_rnn(std::stop_token stoken, const Array& matrix, Result& out_result) {
    std::size_t n = const_cast<Array&>(matrix).getSize();
    if (n < 2) return;

    out_result.cost = std::numeric_limits<int>::max();

    Wektor current_path(n);
    Wektor visited(n);

    // Powtarzamy algorytm zaczynając z każdego możliwego miasta (start_city)
    for (std::size_t start_city = 0; start_city < n; ++start_city) {
        // --- SPRAWDZENIE TIMEOUTU ---
        if (stoken.stop_requested()) return;

        // Reset tablicy odwiedzonych miast dla nowej próby
        for (std::size_t i = 0; i < n; ++i) {
            visited[i] = 0;
        }

        std::size_t current_city = start_city;
        current_path[0] = static_cast<int>(current_city);
        visited[current_city] = 1;

        T current_cost = 0;

        // Budowa trasy (n-1 kroków)
        for (std::size_t step = 1; step < n; ++step) {
            T min_dist = std::numeric_limits<int>::max();
            std::size_t best_next_city = 0;

            for (std::size_t i = 0; i < n; ++i) {
                if (visited[i] == 0) {
                    T dist = const_cast<Array&>(matrix).get(current_city, i);
                    if (dist < min_dist) {
                        min_dist = dist;
                        best_next_city = i;
                    }
                }
            }

            current_path[step] = static_cast<int>(best_next_city);
            visited[best_next_city] = 1;
            current_cost += min_dist;
            current_city = best_next_city;
        }

        // Zamknięcie cyklu (powrót do miasta z którego ruszyliśmy w tej pętli)
        current_cost += const_cast<Array&>(matrix).get(current_city, start_city);

        // Jeśli ta trasa jest lepsza niż poprzednie, zapisujemy ją jako globalnie najlepszą
        if (current_cost < out_result.cost) {
            out_result.cost = current_cost;
            out_result.path = current_path;
        }
    }
}
//=====================================================================================================================

// Funkcja przyjmuje gotową ścieżkę i macierz kosztów, a zwraca całkowity koszt
T calculateTourCost(Wektor& path, const Array& matrix) {
    // Pobieramy rozmiar macierzy
    // (używam const_cast, ponieważ Twoja metoda getSize() nie ma modyfikatora const na końcu)
    std::size_t n = const_cast<Array&>(matrix).getSize();

    if (n < 2) return 0;

    T total_cost = 0;

    // Krok 1: Przejście po wszystkich miastach w ścieżce
    for (std::size_t i = 0; i < n - 1; ++i) {
        // Dodajemy koszt przejścia z miasta i do miasta i+1
        total_cost += const_cast<Array&>(matrix).get(path[i], path[i+1]);
    }

    // Krok 2: Zamknięcie cyklu (powrót z ostatniego miasta do pierwszego)
    total_cost += const_cast<Array&>(matrix).get(path[n-1], path[0]);

    return total_cost;
}

bool verifyVisited(Wektor &path)
{
    return false;
}

//=====================================================================================================================
void tsp_nn_wew(std::stop_token stoken, const Array& matrix, Result& out_result, int start) {
    std::size_t n = const_cast<Array&>(matrix).getSize();
    if (n < 2) return;

    // Przygotowanie wektorów
    Wektor path(n);
    Wektor visited(n);

    // Inicjalizacja tablicy odwiedzin zerami (0 - nieodwiedzone, 1 - odwiedzone)
    for (std::size_t i = 0; i < n; ++i) {
        visited[i] = 0;
    }

    // Zaczynamy od miasta 0 !zawsze
    std::size_t current_city = start;
    path[0] = static_cast<int>(current_city);
    visited[current_city] = 1;

    T total_cost = 0;

    // Szukamy kolejnych n-1 miast
    for (std::size_t step = 1; step < n; ++step) {
        // --- SPRAWDZENIE TIMEOUTU ---
        if (stoken.stop_requested()) return;

        T min_dist = std::numeric_limits<int>::max();
        std::size_t best_next_city = 0;

        // Przeszukujemy wszystkie miasta, aby znaleźć najbliższe nieodwiedzone
        for (std::size_t i = 0; i < n; ++i) {
            if (visited[i] == 0) { // Jeśli jeszcze tu nie byliśmy
                T dist = const_cast<Array&>(matrix).get(current_city, i);
                if (dist < min_dist) {
                    min_dist = dist;
                    best_next_city = i;
                }
            }
        }

        // Przechodzimy do znalezionego miasta
        path[step] = static_cast<int>(best_next_city);
        visited[best_next_city] = 1;
        total_cost += min_dist;
        current_city = best_next_city;
    }

    // Powrót do miasta startowego
    total_cost += const_cast<Array&>(matrix).get(current_city, path[0]);

    // Zapis wyników
    out_result.cost = total_cost;
    out_result.path = path;
}
