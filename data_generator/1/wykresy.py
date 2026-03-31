import os
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# KONFIGURACJA SKRYPTU
# ==========================================
ALGORITHMS = ['random', 'nn', 'rnn']  # Lista badanych algorytmów heurystycznych
N_MIN = 5  # Minimalny rozmiar instancji (N)
N_MAX = 14  # Maksymalny rozmiar instancji (N)

# Przełącznik metryki:
# True  -> Oblicza Błąd Względny (PRD). Wynik idealny to 0%. (Standard w PEA)
# False -> Oblicza Dokładność. Wynik idealny to 100%.
USE_PRD = True

# Ścieżki do folderów
DATA_PATH = "../../test_data/wyniki/"  # Gdzie leżą pliki CSV
OUTPUT_DIR = "wykresy"  # Gdzie zapisać wygenerowane obrazki


def load_data():
    """
    Wczytuje dane z plików CSV, agreguje je (liczy średnie dla każdego N)
    i wylicza błąd względny (PRD) na podstawie wyników Brute Force.
    Zwraca: DataFrame z wynikami heurystyk oraz słownik z czasami Brute Force.
    """
    optimal_costs = {}
    bf_times = {}

    print("[1/2] Wczytywanie wyników Brute Force (wzorce optymalności)...")
    for n in range(N_MIN, N_MAX + 1):
        filename = os.path.join(DATA_PATH, f"brute_force_{n}.csv")

        if os.path.exists(filename):
            # Wczytanie pliku CSV (brak nagłówków, separator to średnik)
            df = pd.read_csv(filename, sep=';', header=None)

            # Wg Twojego C++: kolumna [0] to czas, kolumna [3] to koszt
            optimal_costs[n] = df[3].mean()
            bf_times[n] = df[0].mean()
        else:
            print(f"  -> UWAGA: Brak pliku referencyjnego: {filename}")

    print("[2/2] Wczytywanie wyników algorytmów heurystycznych...")
    heuristic_data = []

    for algo in ALGORITHMS:
        for n in range(N_MIN, N_MAX + 1):
            filename = os.path.join(DATA_PATH, f"{algo}_{n}.csv")

            if os.path.exists(filename):
                df = pd.read_csv(filename, sep=';', header=None)
                avg_time = df[0].mean()
                avg_cost = df[3].mean()

                res_val = None
                # Wyliczamy PRD lub Dokładność, tylko jeśli mamy optymalny koszt z Brute Force
                if n in optimal_costs:
                    if USE_PRD:
                        # Wzór na PRD: ((Koszt_Algorytmu - Koszt_Optymalny) / Koszt_Optymalny) * 100%
                        res_val = ((avg_cost - optimal_costs[n]) / optimal_costs[n]) * 100
                    else:
                        # Wzór na dokładność: (Koszt_Optymalny / Koszt_Algorytmu) * 100%
                        res_val = (optimal_costs[n] / avg_cost) * 100

                # Zapisujemy wiersz do naszej zbiorczej listy
                heuristic_data.append({
                    'n': n,
                    'algo': algo,
                    'time': avg_time,
                    'value': res_val
                })

    # Konwersja listy słowników na wygodną tabelę (DataFrame) biblioteki Pandas
    return pd.DataFrame(heuristic_data), bf_times


def generate_plots(df, bf_times):
    """
    Generuje zestaw wykresów analitycznych na podstawie przygotowanych danych
    i zapisuje je jako pliki .png w zadanym folderze.
    """
    # Upewniamy się, że folder na wykresy istnieje
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Etykieta osi Y zależy od wybranej w konfiguracji metryki
    label_y = "Błąd względny PRD [%]" if USE_PRD else "Dokładność [%]"

    print("\nGenerowanie wykresów...")

    # --- ZESTAW 1: Wykresy punktowe (Scatter) - Porównanie algorytmów dla każdego N ---
    for n in df['n'].unique():
        subset = df[df['n'] == n]

        plt.figure(figsize=(10, 6))
        for algo in subset['algo'].unique():
            s_algo = subset[subset['algo'] == algo]
            # Tworzymy duże punkty (s=200) z czarną obwódką dla lepszej widoczności
            plt.scatter(s_algo['time'], s_algo['value'], label=algo.upper(), s=200, edgecolors='black')

        plt.title(f'Porównanie algorytmów dla N={n}', fontsize=14)
        plt.xlabel('Średni czas wykonania [s]', fontsize=12)
        plt.ylabel(label_y, fontsize=12)
        plt.grid(True, alpha=0.4, linestyle='--')
        plt.legend(title="Algorytm")

        plt.savefig(os.path.join(OUTPUT_DIR, f'1_porownanie_N{n}.png'))
        plt.close()  # Zamykamy wykres, żeby nie zjadał pamięci RAM

    # --- ZESTAW 2: Wykres liniowy - Złożoność czasowa Brute Force (skala logarytmiczna) ---
    if bf_times:
        plt.figure(figsize=(10, 6))

        # Sortujemy dane po N, aby linia szła od lewej do prawej
        ns = sorted(bf_times.keys())
        times = [bf_times[n] for n in ns]

        # Czerwona linia z kwadratowymi znacznikami ('r-s')
        plt.plot(ns, times, 'r-s', linewidth=2, label='Brute Force')

        # KLUCZOWE: Używamy skali logarytmicznej na osi Y, ponieważ czas dla BF rośnie jako O(N!)
        plt.yscale('log')

        plt.title('Złożoność czasowa Brute Force', fontsize=14)
        plt.xlabel('Rozmiar instancji (N)', fontsize=12)
        plt.ylabel('Czas wykonywania [s] (skala logarytmiczna)', fontsize=12)
        plt.grid(True, which="both", ls="--", alpha=0.4)

        plt.savefig(os.path.join(OUTPUT_DIR, '2_zlozonosc_bruteforce.png'))
        plt.close()

    print(f"-> Zapisano wszystkie wykresy w katalogu: '{OUTPUT_DIR}/'")


if __name__ == "__main__":
    print("=== Start Analizy Danych PEA ===")

    # 1. Wczytanie i przetworzenie danych
    df_results, bf_times_dict = load_data()

    # 2. Generowanie wykresów, o ile znaleziono jakiekolwiek dane
    if not df_results.empty:
        generate_plots(df_results, bf_times_dict)
    else:
        print("\n[BŁĄD] Nie znaleziono wystarczającej liczby plików do wygenerowania wykresów.")
        print(f"Sprawdź, czy ścieżka '{DATA_PATH}' jest poprawna i czy pliki istnieją.")

    # 3. Dźwięk zakończenia pracy (Terminal Beep)
    # Działa w większości terminali. Jeśli masz podłączone głośniki w Linuxie, możesz użyć:
    # os.system('speaker-test -t sine -f 800 -l 1 & sleep 0.3 && kill -9 $!')
    print("\a")
    print("=== Koniec ===")