import sys
import random
import itertools
import os
from python_tsp.exact import solve_tsp_dynamic_programming
import numpy as np


def generate_atsp_matrix(n, max_cost):
    """Generuje losową macierz asymetryczną z wartością 999999 na przekątnej."""
    return [[999999 if i == j else random.randint(1, max_cost) for j in range(n)] for i in range(n)]


def solve_held_karp(matrix, n):
    """Rozwiązuje ATSP algorytmem Helda-Karpa w czasie O(N^2 * 2^N)."""
    if n <= 1:
        return 0, [0]

    # C[(maska_odwiedzonych, obecne_miasto)] = (minimalny_koszt, poprzednie_miasto)
    C = {}
    for k in range(1, n):
        C[(1 << k, k)] = (matrix[0][k], 0)

    for subset_size in range(2, n):
        for subset in itertools.combinations(range(1, n), subset_size):
            bits = 0
            for bit in subset:
                bits |= 1 << bit

            for k in subset:
                prev_bits = bits & ~(1 << k)
                res = []
                for m in subset:
                    if m == k:
                        continue
                    res.append((C[(prev_bits, m)][0] + matrix[m][k], m))
                C[(bits, k)] = min(res)

    # Obliczenie powrotu do miasta startowego (0)
    bits = (2 ** n - 1) - 1
    res = []
    for k in range(1, n):
        res.append((C[(bits, k)][0] + matrix[k][0], k))

    opt_cost, last_node = min(res)

    # Odtwarzanie ścieżki
    path = []
    curr_node = last_node
    curr_bits = bits

    for _ in range(n - 1):
        path.append(curr_node)
        new_bits = curr_bits & ~(1 << curr_node)
        curr_node = C[(curr_bits, curr_node)][1]
        curr_bits = new_bits

    path.append(0)
    path.reverse()

    return opt_cost, path


def save_atsp(filename, matrix, n):
    """Zapisuje macierz w formacie TSPLIB."""
    name = os.path.basename(filename).split('.')[0]
    with open(filename, 'w') as f:
        f.write(f"NAME: {name}\n")
        f.write("TYPE: ATSP\n")
        f.write(f"DIMENSION: {n}\n")
        f.write("EDGE_WEIGHT_TYPE: EXPLICIT\n")
        f.write("EDGE_WEIGHT_FORMAT: FULL_MATRIX\n")
        f.write("EDGE_WEIGHT_SECTION\n")
        for row in matrix:
            f.write(" " + " ".join(str(val) for val in row) + "\n")
        f.write("EOF\n")


def save_opt_tour(filename, path, cost, n):
    """Zapisuje trasę w osobnym pliku wg standardu TSPLIB .opt.tour"""
    name = os.path.basename(filename).split('.')[0]
    with open(filename, 'w') as f:
        f.write(f"NAME : {name}.opt.tour\n")
        f.write("TYPE : TOUR\n")
        f.write(f"DIMENSION : {n}\n")
        f.write(f"COMMENT : OPTIMAL_COST = {cost}\n")
        f.write("TOUR_SECTION\n")
        # TSPLIB zazwyczaj indeksuje miasta od 1
        for city in path:
            f.write(f"{city + 1}\n")
        f.write("-1\n")
        f.write("EOF\n")


if __name__ == "__main__":


    for n in range(21, 100):
        max_cost = 100
        base_name = str(n)

        atsp_file = f"{base_name}.atsp"
        tour_file = f"{base_name}.opt.tour"

        matrix = generate_atsp_matrix(n, max_cost)
        opt_cost, best_path = solve_held_karp(matrix, n)
        #best_path, opt_cost = solve_tsp_dynamic_programming(matrix)

        save_atsp(atsp_file, matrix, n)
        save_opt_tour(tour_file, best_path, opt_cost, n)

        print(f"{atsp_file}")
