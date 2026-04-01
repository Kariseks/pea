import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import warnings

# Ignorowanie ostrzeżeń z pandas
warnings.filterwarnings('ignore')

# --- KONFIGURACJA ---
PLIK_WYNIKOW = '../../test_data/wyniki/wyniki.csv'
FOLDER_WYJSCIOWY = '../../sprawko/rys'

# UZUPEŁNIJ: Słownik z optymalnymi kosztami dla instancji z TSPLIB (N > 14)
TSPLIB_OPTYMUM = {
    15: 1234,  # Zmień na prawdziwy koszt
    16: 2345,  # Zmień na prawdziwy koszt
    17: 2085,  # np. gr17.tsp
    21: 2707,  # np. gr21.tsp
    24: 1272,  # np. gr24.tsp
    26: 937,  # np. fri26.tsp
    29: 2020,  # np. bays29.tsp
    # ... dodaj kolejne N, które masz w pliku
}

# Tworzenie folderu wyjściowego, jeśli nie istnieje
os.makedirs(FOLDER_WYJSCIOWY, exist_ok=True)

print("Wczytywanie i przetwarzanie danych...")
kolumny = ['time', 'n', 'algo', 'cost', 'timestamp']
df = pd.read_csv(PLIK_WYNIKOW, sep=';', names=kolumny)

# Wymuszenie typu całkowitego dla 'n'
df['n'] = pd.to_numeric(df['n'], errors='coerce').fillna(0).astype(int)

# Ujednolicenie nazwy algorytmu losowego
df['algo'] = df['algo'].replace('random', 'rand')

# Obliczanie czasu w różnych jednostkach
df['time_us'] = df['time'] * 1e6
df['time_ms'] = df['time'] * 1e3
df['time_min'] = df['time'] / 60.0

# 1. Wyciąganie optymalnych kosztów z algorytmu Brute Force
df_bf = df[df['algo'] == 'brute_force']
optymalne_koszty = df_bf.groupby('n')['cost'].mean().to_dict()


# 2. Obliczanie błędu względnego DLA KAŻDEGO POMIARU
def oblicz_blad_wzgledny(row):
    if row['algo'] == 'brute_force':
        return 0.0

    n = int(row['n'])

    # Bezpieczne rzutowanie kosztu na float
    try:
        koszt_aktualny = float(row['cost'])
    except (ValueError, TypeError):
        return None

    # Wybór źródła optymalnego kosztu
    if n <= 14:
        koszt_optymalny = optymalne_koszty.get(n)
    else:
        koszt_optymalny = TSPLIB_OPTYMUM.get(n)

    if koszt_optymalny and float(koszt_optymalny) > 0:
        koszt_optymalny = float(koszt_optymalny)
        # Błąd względny (|koszt_uzyskany - koszt_optymalny| / koszt_optymalny) * 100%
        # Użyto abs() aby uniknąć błędów ujemnych jeśli z jakiegoś powodu koszt jest mniejszy
        return (abs(koszt_aktualny - koszt_optymalny) / koszt_optymalny) * 100.0
    return None


df['rel_error'] = df.apply(oblicz_blad_wzgledny, axis=1)

# DIAGNOSTYKA W KONSOLI (Żebyś widział(a) na własne oczy, czy działa poprawnie)
print("\n--- DIAGNOSTYKA: PRZYKŁADOWE WYLICZENIA BŁĘDU ---")
df_debug = df[df['algo'] != 'brute_force'].dropna(subset=['rel_error'])
if not df_debug.empty:
    print(df_debug[['n', 'algo', 'cost', 'rel_error']].head(10))
else:
    print("OSTRZEŻENIE: Brak danych do wyświetlenia (wszystkie błędy to NaN). Sprawdź słownik TSPLIB.")
print("-------------------------------------------------\n")

# 3. Uśrednianie wyników podstawowych
df_srednie = df.groupby(['n', 'algo'])[['time', 'rel_error']].mean().reset_index()
df_heur_srednie = df_srednie[df_srednie['n'] >= 5]

# ==========================================
# GENEROWANIE TABEL
# ==========================================
print("Generowanie tabel CSV...")

df_czasy = df_srednie[df_srednie['algo'] != 'rand']
tabela_czasow = df_czasy.pivot(index='n', columns='algo', values='time')
kolumny_dostepne = [col for col in ['nn', 'rnn', 'bruteforce'] if col in tabela_czasow.columns]
tabela_czasow = tabela_czasow[kolumny_dostepne]
tabela_czasow = tabela_czasow * 1e6
tabela_czasow.to_csv(f'{FOLDER_WYJSCIOWY}/tabela_czasow.csv', float_format='%.4g')

df_rand = df[df['algo'] == 'rand'].copy()

bins_macro = list(range(0, 65, 5)) + [120, 180, 240, 300]
labels_macro = [f"{i}-{i + 5}s" for i in range(0, 60, 5)] + ["1-2m", "2-3m", "3-4m", "4-5m"]
df_rand['binmacro'] = pd.cut(df_rand['time'], bins=bins_macro, labels=labels_macro)
tabela_rand_macro = df_rand.groupby(['binmacro', 'n'])['rel_error'].mean().unstack()
tabela_rand_macro.dropna(how='all', inplace=True)
# ZMIANA: Zapis do 4 miejsc po przecinku, żeby nie zaokrąglało bardzo małych błędów do zera
tabela_rand_macro.to_csv(f'{FOLDER_WYJSCIOWY}/tabela_rand_macro.csv', float_format='%.4f')

bins_micro = list(range(10, 52, 1))
labels_micro = [f"{i}us" for i in range(10, 51)]
df_rand['binmicro'] = pd.cut(df_rand['time_us'], bins=bins_micro, labels=labels_micro)
tabela_rand_micro = df_rand.groupby(['binmicro', 'n'])['rel_error'].mean().unstack()
tabela_rand_micro.dropna(how='all', inplace=True)
tabela_rand_micro.to_csv(f'{FOLDER_WYJSCIOWY}/tabela_rand_micro.csv', float_format='%.4f')

# ---------------------------------------------------------
# DODATKOWE TABELE ZGODNIE Z PROŚBĄ
# ---------------------------------------------------------

# 1. Tabela z czasami obliczeń (średnimi) tylko dla Brute Force
nazwa_indeksu_bf = 'Rozmiar (N)'
kolumna_czas_bf = 'Średni czas obliczeń'

print("Generowanie tabeli LaTeX dla Brute Force...")
df_bf_latex = df_srednie[df_srednie['algo'] == 'brute_force'][['n', 'time']].copy()
df_bf_latex['time'] = df_bf_latex['time'] * 1e6
naglowek_z_jednostka = f"{kolumna_czas_bf} [µs]"

df_bf_latex.rename(columns={'time': naglowek_z_jednostka}, inplace=True)
df_bf_latex.set_index('n', inplace=True)
df_bf_latex.index.name = nazwa_indeksu_bf

kod_latex = df_bf_latex.to_latex(
    index=True,
    column_format='|c|c|',
    bold_rows=True,
    float_format="%.4f",
    caption="Średnie czasy wykonania algorytmu Brute Force",
    label="tab:bf_times"
)

with open(f'{FOLDER_WYJSCIOWY}/tabela_bf.tex', 'w', encoding='utf-8') as f:
    f.write(kod_latex)

print(" -> Wygenerowano plik LaTeX: tabela_bf.tex")

print("Generowanie tabeli czasu dla Brute Force...")
df_bf_czasy = df_srednie[df_srednie['algo'] == 'brute_force'][['n', 'time']].copy()
df_bf_czasy.rename(columns={'time': 'timeavgs'}, inplace=True)
df_bf_czasy.set_index('n', inplace=True)
df_bf_czasy.to_csv(f'{FOLDER_WYJSCIOWY}/tabela_czasow_bf.csv', float_format='%.4g')

# 2. Tabela ze statystykami rozrzutu błędu względnego dla RAND (N=14)
print("Generowanie tabeli statystyk i rozrzutu dla RAND (N=14)...")
df_rand_14 = df[(df['algo'] == 'rand') & (df['n'] == 14)].copy()
df_rand_14['..'] = pd.cut(df_rand_14['time'], bins=bins_macro, labels=labels_macro)

tabela_rand_14_statystyki = df_rand_14.groupby('..')['rel_error'].agg(
    sredni_blad='mean',
    odchyleniestd='std',
    minimum='min',
    maksimum='max',
    liczbapomiarow='count'
)
tabela_rand_14_statystyki.dropna(subset=['sredni_blad'], inplace=True)
tabela_rand_14_statystyki.to_csv(f'{FOLDER_WYJSCIOWY}/tabela_rand_14_rozrzut.csv', float_format='%.4f')

# ==========================================
# WYKRESY
# ==========================================
print("Generowanie wykresów...")

# WYKRES 1: Brute Force
plt.figure(figsize=(8, 6))
bf_srednie = df_srednie[df_srednie['algo'] == 'brute_force'].sort_values(by='n')
plt.plot(bf_srednie['n'], bf_srednie['time'], marker='o', color='red', linewidth=2)
plt.title('Czas obliczeń Brute Force w funkcji wielkości instancji')
plt.xlabel('Rozmiar instancji (N)')
plt.ylabel('Średni czas obliczeń [s]')
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(f'{FOLDER_WYJSCIOWY}/brute_force.pdf', bbox_inches='tight')
plt.close()

# ==========================================
# NOWY WYKRES: RAND - WSZYSTKIE INSTANCJE (Minuty, Zwykła legenda)
# ==========================================
df_rand_wszystkie = df[(df['algo'] == 'rand') & (df['n'] >= 5)]
if not df_rand_wszystkie.empty:
    plt.figure(figsize=(10, 6))

    unikalne_n = sorted(df_rand_wszystkie['n'].unique())
    paleta = plt.get_cmap('tab10' if len(unikalne_n) <= 10 else 'tab20')
    kolory = [paleta(i) for i in np.linspace(0, 1, len(unikalne_n))]

    for i, n_val in enumerate(unikalne_n):
        dane_n = df_rand_wszystkie[df_rand_wszystkie['n'] == n_val]
        plt.scatter(dane_n['time_min'], dane_n['rel_error'],
                    label=f'N={n_val}', color=kolory[i],
                    alpha=0.6, edgecolors='none', s=40)

    plt.title('Błąd względny RAND (Wszystkie instancje)')
    plt.xlabel('Czas pomiaru [minuty]')
    plt.ylabel('Błąd względny [%]')
    plt.ylim(bottom=0)

    plt.legend(title='Rozmiar instancji', loc='upper right', ncol=2, fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.5, which='both')
    plt.tight_layout()
    plt.savefig(f'{FOLDER_WYJSCIOWY}/rand_wszystkie_instancje_calosc_minuty.png')
    plt.savefig(f'{FOLDER_WYJSCIOWY}/rand_wszystkie_instancje_calosc_minuty.pdf')
    plt.close()
    print(" -> Wygenerowano: Wykres RAND dla wszystkich instancji (w minutach)")

# ==========================================
# WYKRES: NN, RNN i RAND (TYLKO N=14, 10-50 us, SKALA LINIOWA)
# ==========================================
df_rand_14 = df_rand[df_rand['n'] == 14]

plt.figure(figsize=(10, 6))
algorytmy_deterministyczne = {'nn': 'blue', 'rnn': 'green'}

for algo, kolor in algorytmy_deterministyczne.items():
    dane_algo = df_heur_srednie[df_heur_srednie['algo'] == algo]
    if not dane_algo.empty:
        plt.scatter(dane_algo['time'] * 1e6, dane_algo['rel_error'],
                    label=algo.upper(), color=kolor, s=100, alpha=0.7, edgecolors='black', zorder=3)
        for _, row in dane_algo.iterrows():
            plt.annotate(f"{int(row['n'])}", (row['time'] * 1e6, row['rel_error']),
                         textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8)

dane_rand_micro = df_rand_14[(df_rand_14['time_us'] >= 10) & (df_rand_14['time_us'] <= 50)].copy()
if not dane_rand_micro.empty:
    plt.scatter(dane_rand_micro['time_us'], dane_rand_micro['rel_error'],
                color='yellow', label='RAND N=14 (wszystkie punkty)',
                alpha=0.6, edgecolors='black', s=40, zorder=2)

plt.title('Błąd względny algorytmów niedokładnych w funkcji wielkości instancji')
plt.xlabel('Czas obliczeń [µs]')
plt.ylabel('Błąd względny [%]')
plt.xlim(10, 50)
plt.ylim(bottom=0)
plt.legend(loc='upper right')
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(f'{FOLDER_WYJSCIOWY}/dokladnosc_czas_nn_rnn_rand_liniowa_10_50us.png', bbox_inches='tight')
plt.savefig(f'{FOLDER_WYJSCIOWY}/dokladnosc_czas_nn_rnn_rand_liniowa_10_50us.pdf', bbox_inches='tight')
plt.close()

# ===========================================================================================
# WYKRES: Czas NN i RNN vs N
plt.figure(figsize=(8, 6))
for algo in ['nn', 'rnn']:
    dane_algo = df_srednie[df_srednie['algo'] == algo].sort_values(by='n')
    plt.plot(dane_algo['n'], dane_algo['time'] * 1e6, marker='s', label=algo.upper(), linewidth=2)
plt.title('Czas obliczeń dla NN i RNN w funkcji wielkości instancji')
plt.xlabel('Rozmiar instancji (N)')
plt.ylabel('Średni czas obliczeń [us]')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(f'{FOLDER_WYJSCIOWY}/czas_nn_rnn_vs_n.png', bbox_inches='tight')
plt.savefig(f'{FOLDER_WYJSCIOWY}/czas_nn_rnn_vs_n.pdf', bbox_inches='tight')
plt.close()

# ==========================================
# WYKRES RAND (WSZYSTKIE INSTANCJE) W PRZEDZIALE 0.0 ms - 1.0 ms
# ==========================================
df_rand_zoom = df[(df['algo'] == 'rand') & (df['n'] >= 5)].copy()
df_rand_zoom['time_ms'] = df_rand_zoom['time'] * 1000
df_rand_zoom = df_rand_zoom[(df_rand_zoom['time_ms'] >= 0.0) & (df_rand_zoom['time_ms'] <= 1.0)]

print(f"\n--- Analiza RAND (0.0 ms - 1.0 ms) ---")
print(f"Liczba punktów w tym przedziale: {len(df_rand_zoom)}")

if not df_rand_zoom.empty:
    plt.figure(figsize=(10, 6))

    unikalne_n = sorted(df_rand_zoom['n'].unique())
    paleta = plt.get_cmap('tab10' if len(unikalne_n) <= 10 else 'tab20')
    kolory = [paleta(i) for i in np.linspace(0, 1, len(unikalne_n))]

    for i, n_val in enumerate(unikalne_n):
        dane_n = df_rand_zoom[df_rand_zoom['n'] == n_val]
        plt.scatter(dane_n['time_ms'], dane_n['rel_error'],
                    label=f'N={n_val}', color=kolory[i],
                    alpha=0.7, edgecolors='black', s=60, zorder=3)

    plt.title('Błąd względny RAND - Wszystkie instancje (0.0 ms do 1.0 ms)')
    plt.xlabel('Czas pomiaru [ms]')
    plt.ylabel('Błąd względny [%]')

    plt.xlim(0, 1.0)
    plt.ylim(bottom=0)

    plt.legend(title='Rozmiar instancji', loc='upper right', ncol=2, fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.5, which='both')
    plt.tight_layout()

    plt.savefig(f'{FOLDER_WYJSCIOWY}/rand_wszystkie_0_1ms.png')
    plt.savefig(f'{FOLDER_WYJSCIOWY}/rand_wszystkie_0_1ms.pdf')
    plt.close()
    print(f" -> Wygenerowano wykres: rand_wszystkie_0_1ms.png")
else:
    print(" -> BŁĄD: Brak danych dla RAND w przedziale 0.0 - 1.0 ms!")

# ==========================================
# NOWE WYKRESY: RAND N=14 (SKALA LOGARYTMICZNA ORAZ DYNAMICZNE JEDNOSTKI)
# ==========================================
df_rand_14_all = df[(df['algo'] == 'rand') & (df['n'] == 14)].copy()
df_rand_14_all = df_rand_14_all.dropna(subset=['rel_error'])

print(f"\n--- Generowanie nowych wykresów dla RAND N=14 ---")

if not df_rand_14_all.empty:
    # ---------------------------------------------------------
    # 1. Pełny zakres - Skala logarytmiczna
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.scatter(df_rand_14_all['time'], df_rand_14_all['rel_error'],
                color='purple', alpha=0.6, s=40, edgecolors='black')
    plt.xscale('log')
    plt.title('Błąd względny RAND N=14 (Pełny zakres - Skala logarytmiczna)')
    plt.xlabel('Czas pomiaru [s] (skala logarytmiczna)')
    plt.ylabel('Błąd względny [%]')
    plt.ylim(bottom=0)
    plt.grid(True, linestyle='--', alpha=0.5, which='both')
    plt.tight_layout()
    plt.savefig(f'{FOLDER_WYJSCIOWY}/rand_n14_log_pelny.png')
    plt.close()
    print(" -> Wygenerowano: Skala logarytmiczna (pełny zakres w sekundach)")

    # ---------------------------------------------------------
    # 2. Wykresy dla konkretnych przedziałów z dopasowaną jednostką
    # ---------------------------------------------------------
    przedzialy = [
        (0.0, 0.001, 1e6, '0_do_1000_us', 'µs', 0, 1000),
        (0.001, 0.1, 1e3, '1_do_100_ms', 'ms', 1, 100),
        (0.1, 1.0, 1e3, '100_do_1000_ms', 'ms', 100, 1000),
        (1.0, 60.0, 1.0, '1_do_60_s', 's', 1, 60),
        (60.0, 600.0, 1 / 60.0, '1_do_10_min', 'min', 1, 10)
    ]

    for t_min, t_max, mnoznik, nazwa, jednostka, x_min, x_max in przedzialy:
        if t_min == 0.0:
            dane_przedzial = df_rand_14_all[(df_rand_14_all['time'] >= t_min) & (df_rand_14_all['time'] <= t_max)]
        else:
            dane_przedzial = df_rand_14_all[(df_rand_14_all['time'] > t_min) & (df_rand_14_all['time'] <= t_max)]

        plt.figure(figsize=(10, 6))

        if not dane_przedzial.empty:
            czas_przeskalowany = dane_przedzial['time'] * mnoznik
            plt.scatter(czas_przeskalowany, dane_przedzial['rel_error'],
                        color='orange', alpha=0.7, s=50, edgecolors='black')
            print(
                f" -> Wygenerowano: Przedział {x_min} - {x_max} {jednostka} (znaleziono {len(dane_przedzial)} punktów)")
        else:
            plt.text(0.5, 0.5, f'Brak wyników w pliku dla zakresu {x_min} - {x_max} {jednostka}',
                     ha='center', va='center', fontsize=14, color='red', transform=plt.gca().transAxes)
            print(f" -> Wygenerowano PUSTY: Przedział {x_min} - {x_max} {jednostka} (0 punktów)")

        plt.xlim(x_min, x_max)
        plt.ylim(bottom=0)

        plt.title(f'Błąd względny RAND N=14 (Zakres: {x_min} do {x_max} {jednostka})')
        plt.xlabel(f'Czas pomiaru [{jednostka}]')
        plt.ylabel('Błąd względny [%]')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(f'{FOLDER_WYJSCIOWY}/rand_n14_{nazwa}.png')
        plt.close()
else:
    print(" -> BŁĄD: Brak danych dla RAND N=14 do narysowania wykresów!")
print(f"\nGotowe! Pliki zapisane w: {FOLDER_WYJSCIOWY}/")