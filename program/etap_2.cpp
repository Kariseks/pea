#include "etap_2.h"
#include "etap_1.h"
#include "nodepriorityqueue.h"
#include "nodequeue.h"

using namespace std;
using namespace pea;

#include "node.h"
#include "nodestack.h"
#include <climits>

namespace
{


}


const T INF = std::numeric_limits<T>::max() / 2; // Zapobiega przepełnieniu przy dodawaniu

// Zwraca koszt redukcji macierzy
T reduce_matrix(pea::Array& m) {
    T reduction_cost = 0;
    int n = m.getSize();

    // 1. Redukcja wierszy
    for (int i = 0; i < n; ++i) {
        T min_val = INF;
        for (int j = 0; j < n; ++j) {
            if (m.get(i, j) < min_val) min_val = m.get(i, j);
        }
        if (min_val != INF && min_val > 0) {
            reduction_cost += min_val;
            for (int j = 0; j < n; ++j) {
                if (m.get(i, j) != INF) {
                    m.set(m.get(i, j) - min_val, i, j);
                }
            }
        }
    }

    // 2. Redukcja kolumn
    for (int j = 0; j < n; ++j) {
        T min_val = INF;
        for (int i = 0; i < n; ++i) {
            if (m.get(i, j) < min_val) min_val = m.get(i, j);
        }
        if (min_val != INF && min_val > 0) {
            reduction_cost += min_val;
            for (int i = 0; i < n; ++i) {
                if (m.get(i, j) != INF) {
                    m.set(m.get(i, j) - min_val, i, j);
                }
            }
        }
    }

    return reduction_cost;
}

Result deep_first_search(const pea::Array& matrix) {
    int n = matrix.getSize();

    // 1. Wyznaczenie początkowego UB za pomocą algorytmu zachłannego z etapu 1
    Result best_result = tsp_rnn(matrix);
    T UB = best_result.cost;

    NodeStack stack;    // kolejka LIFO

    // 2. Inicjalizacja korzenia
    Node root(n);
    root.path[0] = 0; // BEZPIECZNE PRZYPISANIE zamiast push_back
    root.visited[0] = true;
    root.level = 1;

    // Kopiujemy macierz pierwotną i blokujemy przekątną
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            if (i == j) root.reduceMatrix.set(INF, i, j);
            else root.reduceMatrix.set(matrix.get(i, j), i, j);
        }
    }

    // Pierwsza redukcja algorytmem Little'a
    root.bound = reduce_matrix(root.reduceMatrix);
    stack.push(std::move(root));

    // 3. Główna pętla DFS
    while (!stack.empty()) {
        Node currentNode = std::move(stack.top());
        stack.pop();

        // Pruning (odcięcie gałęzi)
        if (currentNode.bound >= UB) continue;

        // Pobranie ostatnio odwiedzonego wierzchołka (indeks to level - 1)
        int i = currentNode.path[currentNode.level - 1];

        // Sprawdzenie, czy dotarliśmy do liścia (pełna ścieżka)
        if (currentNode.level == n) {
            T final_cost = currentNode.bound;

            if (final_cost < UB) {
                UB = final_cost;
                best_result.cost = UB;

                // BEZPIECZNE KOPIOWANIE ścieżki do najlepszego wyniku
                for(int p = 0; p < n; p++) {
                    best_result.path[p] = currentNode.path[p];
                }
            }
            continue;
        }

        // 4. Generowanie dzieci (kolejne nieodwiedzone miasta)
        for (int j = n - 1; j >= 0; --j) {
            if (!currentNode.visited[j]) {
                T cost_ij = currentNode.reduceMatrix.get(i, j);
                if (cost_ij == INF) continue;

                Node child(currentNode); // Wywołanie konstruktora kopiującego

                // BEZPIECZNE PRZYPISANIE kolejnego wierzchołka
                child.path[child.level] = j;
                child.visited[j] = true;
                child.level++;

                // Algorytm Little'a: przygotowanie macierzy dla dziecka
                for (int k = 0; k < n; ++k) {
                    child.reduceMatrix.set(INF, i, k); // Wykreślamy wiersz 'i'
                    child.reduceMatrix.set(INF, k, j); // Wykreślamy kolumnę 'j'
                }
                // Zapobieganie przedwczesnemu powrotowi do startu (sub-tours)
                child.reduceMatrix.set(INF, j, 0);

                // Redukcja i aktualizacja ograniczenia (LB)
                T reduction = reduce_matrix(child.reduceMatrix);
                child.bound = currentNode.bound + cost_ij + reduction;

                // Dodajemy na stos tylko obiecujące węzły
                if (child.bound < UB) {
                    stack.push(std::move(child));
                }
            }
        }
    }
    return best_result;
}


/*
Result deep_first_search(const pea::Array & matrix)
{
    //#1 wyznaczenie UB, żeby juz w pierwszym przebiegu wycinać nie rokujące ścieżki
    auto ub_res = tsp_rnn(matrix);

    //#2 Stowrzenie koleji LIFO na Node
    Stack stack{rozmiar};

    //#2 Inicjalizacja root Node,

    // Główna pętla programu
    while(! stack.is_empty())
    {

        uint64_t to_visit = ~visited_cities & ((1ULL << N) - 1); // Maska nieodwiedzonych miast

        while (to_visit > 0) {
            // Sprzętowo znajdź indeks pierwszej jedynki (następne wolne miasto)
            int city_index = __builtin_ctzll(to_visit);

            // Wykonaj logikę dla tego miasta...
            std::cout << "Sprawdzam miasto nr: " << city_index << std::endl;

            // Usuń tę jedynkę z maski, aby w następnym obrocie znaleźć kolejną
            // (Operacja bitowa: liczba AND (liczba - 1) kasuje najniższą jedynkę)
            to_visit &= (to_visit - 1);
        }
    }


}
*/
Result best_first_search(const pea::Array& matrix) {
    int n = matrix.getSize();

    // 1. Wyznaczenie początkowego UB za pomocą algorytmu zachłannego
    Result best_result = tsp_rnn(matrix);
    T UB = best_result.cost;

    // Kolejka priorytetowa (zawsze zwraca Node z najmniejszym 'bound')
    NodePriorityQueue pq;

    // 2. Inicjalizacja korzenia
    Node root(n);
    root.path[0] = 0; // BEZPIECZNE PRZYPISANIE zamiast push_back
    root.visited[0] = true;
    root.level = 1;

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            if (i == j) root.reduceMatrix.set(INF, i, j);
            else root.reduceMatrix.set(matrix.get(i, j), i, j);
        }
    }

    // Pierwsza redukcja algorytmem Little'a
    root.bound = reduce_matrix(root.reduceMatrix);
    pq.push(std::move(root));

    // 3. Główna pętla Best-First Search
    while (!pq.empty()) {
        Node current = std::move(pq.top());
        pq.pop();

        // Pruning (odcięcie gałęzi).
        // Jeśli pobrany element z najniższym priorytetem jest gorszy/równy niż UB,
        // to cała reszta kolejki też jest gorsza i można teoretycznie zakończyć!
        if (current.bound >= UB) {
            // W idealnym scenariuszu Best-First, jeśli najmniejszy bound >= UB,
            // lepszego wyniku już nie znajdziemy. Można tu nawet zrobić break.
            break;
        }

        int i = current.path[current.level - 1];

        // Sprawdzenie, czy dotarliśmy do liścia (pełna ścieżka)
        if (current.level == n) {
            T final_cost = current.bound;

            if (final_cost < UB) {
                UB = final_cost;
                best_result.cost = UB;

                // BEZPIECZNE KOPIOWANIE ścieżki do najlepszego wyniku
                for(int p = 0; p < n; p++) {
                    best_result.path[p] = current.path[p];
                }
            }
            continue;
        }

        // 4. Generowanie dzieci (kolejne nieodwiedzone miasta)
        for (int j = 0; j < n; ++j) {
            if (!current.visited[j]) {
                T cost_ij = current.reduceMatrix.get(i, j);
                if (cost_ij == INF) continue;

                Node child(current);

                // BEZPIECZNE PRZYPISANIE kolejnego wierzchołka
                child.path[child.level] = j;
                child.visited[j] = true;
                child.level++;

                // Algorytm Little'a
                for (int k = 0; k < n; ++k) {
                    child.reduceMatrix.set(INF, i, k);
                    child.reduceMatrix.set(INF, k, j);
                }
                child.reduceMatrix.set(INF, j, 0);

                // Redukcja i aktualizacja (LB)
                T reduction = reduce_matrix(child.reduceMatrix);
                child.bound = current.bound + cost_ij + reduction;

                // Dodajemy na kolejkę priorytetową tylko obiecujące węzły
                if (child.bound < UB) {
                    pq.push(std::move(child));
                }
            }
        }
    }

    return best_result;
}

Result breadth_first_search(const pea::Array& matrix) {
    int n = matrix.getSize();

    // 1. Wyznaczenie początkowego UB za pomocą algorytmu zachłannego
    Result best_result = tsp_rnn(matrix);
    T UB = best_result.cost;

    NodeQueue queue;

    // 2. Inicjalizacja korzenia
    Node root(n);

    // BEZPIECZNE PRZYPISANIE (zamiast push_back)
    // Ponieważ Wektor(n) już ustawił size na 'n', podmieniamy tylko śmieci pod indeksem 0
    root.path[0] = 0;
    root.visited[0] = true;
    root.level = 1;

    // Kopiujemy macierz pierwotną i blokujemy przekątną
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            if (i == j) root.reduceMatrix.set(INF, i, j);
            else root.reduceMatrix.set(matrix.get(i, j), i, j);
        }
    }

    // Pierwsza redukcja algorytmem Little'a
    root.bound = reduce_matrix(root.reduceMatrix);

    // Bezpieczne kopiowanie do kolejki (omijamy std::move, żeby uniknąć segfaultów sterty)
    queue.push(root);

    // 3. Główna pętla BFS
    while (!queue.empty()) {
        // Znowu bezpieczna kopia
        Node current = queue.front();
        queue.pop();

        // Pruning (odcięcie gałęzi)
        if (current.bound >= UB) continue;

        // Pobranie ostatnio odwiedzonego wierzchołka z bezpiecznego indeksu
        int i = current.path[current.level - 1];

        // Sprawdzenie, czy dotarliśmy do liścia (pełna ścieżka)
        if (current.level == n) {
            T final_cost = current.bound;

            if (final_cost < UB) {
                UB = final_cost;
                best_result.cost = UB;

                // Ręczne, bezpieczne kopiowanie ścieżki do najlepszego wyniku
                for(int p = 0; p < n; p++) {
                    best_result.path[p] = current.path[p];
                }
            }
            continue;
        }

        // 4. Generowanie dzieci (kolejne nieodwiedzone miasta)
        for (int j = 0; j < n; ++j) {
            if (!current.visited[j]) {
                T cost_ij = current.reduceMatrix.get(i, j);
                if (cost_ij == INF) continue;

                Node child(current); // Konstruktor kopiujący struktury Node

                // BEZPIECZNE PRZYPISANIE DO WĘZŁA
                // Wpisujemy kolejne miasto w odpowiednie, puste jeszcze miejsce w ścieżce
                child.path[child.level] = j;
                child.visited[j] = true;
                child.level++;

                // Algorytm Little'a: przygotowanie macierzy dla dziecka
                for (int k = 0; k < n; ++k) {
                    child.reduceMatrix.set(INF, i, k);
                    child.reduceMatrix.set(INF, k, j);
                }
                child.reduceMatrix.set(INF, j, 0);

                // Redukcja i aktualizacja ograniczenia (LB)
                T reduction = reduce_matrix(child.reduceMatrix);
                child.bound = current.bound + cost_ij + reduction;

                // Dodajemy do kolejki tylko obiecujące węzły
                if (child.bound < UB) {
                    queue.push(child); // Bezpieczna kopia do kolejki
                }
            }
        }
    }

    return best_result;
}