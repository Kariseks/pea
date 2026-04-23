import os
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# KONFIGURACJA SKRYPTU
# ==========================================
# Nazwy algorytmów dokładnie takie, jak zapisuje je Twój program C++ w kolumnie 'algo'
ALGORITHMS = ['random', 'nn', 'rnn']
BF_ALGO_NAME = 'bf'  # Nazwa algorytmu Brute Force w pliku CSV (zmień na 'brute_force' jeśli tak masz)

N_MIN = 5
N_MAX = 14

USE_PRD = True  # True = Błąd Względny [%], False = Dokładność [%]

DATA_PATH = "../../test_data/wyniki/"  # Folder z plikami <n>_wyniki.csv
OUTPUT_DIR = "wykresy"  # Folder wyjściowy na obrazki


def load_data():
    """
    Wczytuje pliki w formacie <n>_wyniki.csv, gdzie każdy plik zawiera
    wymieszane wyniki dla różnych algorytmów.
    """
    optimal_costs = {}
    bf_times = {}
    heuristic_data = []

    print("[1/2] Wczytywanie i przetwarzanie plików z wynikami...")

    for n in range(N_MIN, N_MAX + 1):
        filename = os.path.join(DATA_PATH, f"{n}_wyniki.csv")

        if not os.path.exists(filename):
            print(f"  -> UWAGA: Brak pliku: {filename}")
            continue

        # Wczytujemy cały plik dla danego N.
        # Nadajemy nazwy kolumnom dla łatwiejszego filtrowania: time, n, algo, cost, timestamp
        df = pd.read_csv(filename, sep=';', header=None,
                         names=['time', 'n', 'algo', 'cost', 'timestamp'])

        # Standaryzacja nazw algorytmów (usuwamy spacje, zamieniamy na małe litery),
        # żeby uniknąć błędów typu " nn" vs "nn"
        df['algo'] = df['algo'].astype(str).str.strip().str.lower()

        # 1. Wyciąganie wyników referencyjnych (Brute Force)
        df_bf = df[df['algo'] == BF_ALGO_NAME]
        if not df_bf.empty:
            optimal_costs[n] = df_bf['cost'].mean()
            bf_times[n] = df_bf['time'].mean()
        else:
            print(
                f"  -> UWAGA: W pliku {n}_wyniki.csv brakuje wyników dla {BF_ALGO_NAME}! Obliczenie błędu będzie niemożliwe.")

        # 2. Wyciąganie wyników dla algorytmów heurystycznych
        for algo in ALGORITHMS:
            df_algo = df[df['algo'] == algo]

            if not df_algo.empty:
                avg_time = df_algo['time'].mean()
                avg_cost = df_algo['cost'].mean()

                res_val = None
                # Wyliczamy błąd tylko, jeśli mamy znalezione optimum (Brute Force) dla tego N
                if n in optimal_costs:
                    opt_cost = optimal_costs[n]
                    if USE_PRD:
                        res_val = ((avg_cost - opt_cost) / opt_cost) * 100
                    else:
                        res_val = (opt_cost / avg_cost) * 100

                heuristic_data.append({
                    'n': n,
                    'algo': algo,
                    'time': avg_time,
                    'value': res_val
                })

    return pd.DataFrame(heuristic_data), bf_times


def generate_plots(df, bf_times):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    label_y = "Błąd względny PRD [%]" if USE_PRD else "Dokładność [%]"

    print("\n[2/2] Generowanie wykresów...")

    # --- ZESTAW 1: Wykresy punktowe (Scatter) - Jakość vs Czas dla każdego N ---
    for n in df['n'].unique():
        subset = df[df['n'] == n]
        if subset['value'].isnull().all(): continue  # Pomijamy, jeśli nie ma wyliczonego błędu

        plt.figure(figsize=(10, 6))
        for algo in subset['algo'].unique():
            s_algo = subset[subset['algo'] == algo]
            plt.scatter(s_algo['time'], s_algo['value'], label=algo.upper(), s=200, edgecolors='black')

        plt.title(f'Porównanie algorytmów dla N={n}', fontsize=14)
        plt.xlabel('Średni czas wykonania [s]', fontsize=12)
        plt.ylabel(label_y, fontsize=12)
        plt.grid(True, alpha=0.4, linestyle='--')
        plt.legend(title="Algorytm")
        plt.savefig(os.path.join(OUTPUT_DIR, f'1_jakosc_vs_czas_N{n}.png'))
        plt.close()

    # --- ZESTAW 2: Wykres liniowy - Jakość w zależności od rozmiaru problemu (N) ---
    # To jest najważniejszy wykres analityczny na projekt!
    plt.figure(figsize=(10, 6))
    for algo in df['algo'].unique():
        subset = df[df['algo'] == algo].sort_values(by='n')
        # Rysujemy tylko te punkty, które mają wyliczoną wartość (nie są NaN)
        subset = subset.dropna(subset=['value'])

        if not subset.empty:
            plt.plot(subset['n'], subset['value'], marker='o', linewidth=2, markersize=8, label=algo.upper())

    plt.title('Zależność jakości rozwiązań od wielkości problemu (N)', fontsize=14)
    plt.xlabel('Rozmiar instancji (N)', fontsize=12)
    plt.ylabel(label_y, fontsize=12)
    plt.xticks(range(N_MIN, N_MAX + 1))  # Wymusza równe odstępy na osi X
    plt.grid(True, alpha=0.4, linestyle='--')
    plt.legend(title="Algorytm")
    plt.savefig(os.path.join(OUTPUT_DIR, '2_jakosc_vs_N.png'))
    plt.close()

    # --- ZESTAW 3: Wykres liniowy - Złożoność czasowa Brute Force ---
    if bf_times:
        plt.figure(figsize=(10, 6))
        ns = sorted(bf_times.keys())
        times = [bf_times[n] for n in ns]

        plt.plot(ns, times, 'r-s', linewidth=2, markersize=8, label='Brute Force')
        plt.yscale('log')  # Skala logarytmiczna

        plt.title('Złożoność czasowa algorytmu dokładnego (Brute Force)', fontsize=14)
        plt.xlabel('Rozmiar instancji (N)', fontsize=12)
        plt.ylabel('Czas wykonywania [s] (skala logarytmiczna)', fontsize=12)
        plt.xticks(ns)
        plt.grid(True, which="both", ls="--", alpha=0.4)

        plt.savefig(os.path.join(OUTPUT_DIR, '3_czas_bruteforce.png'))
        plt.close()

    print(f"-> Zapisano wszystkie wykresy w katalogu: '{OUTPUT_DIR}/'")


if __name__ == "__main__":
    print("=== Start Analizy Danych ===")

    df_results, bf_times_dict = load_data()

    if not df_results.empty:
        generate_plots(df_results, bf_times_dict)
    else:
        print("\n[BŁĄD] Nie wczytano żadnych danych heurystycznych. Sprawdź ścieżki i zawartość plików.")

    print("\a")  # Dźwięk zakończenia
    print("=== Koniec ===")