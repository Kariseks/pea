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

# Tworzenie folderu wyjściowego, jeśli nie istnieje
os.makedirs(FOLDER_WYJSCIOWY, exist_ok=True)

print("Wczytywanie i przetwarzanie danych...")
kolumny = ['time', 'n', 'algo', 'cost', 'timestamp']
df = pd.read_csv(PLIK_WYNIKOW, sep=';', names=kolumny)

# Ujednolicenie nazwy algorytmu losowego
df['algo'] = df['algo'].replace('random', 'rand')

# Obliczanie czasu w mikrosekundach i milisekundach dla wykresów przedziałowych
df['time_us'] = df['time'] * 1e6
df['time_ms'] = df['time'] * 1e3

# 1. Wyciąganie optymalnych kosztów z algorytmu Brute Force
df_bf = df[df['algo'] == 'brute_force']
optymalne_koszty = df_bf.groupby('n')['cost'].mean().to_dict()


# 2. Obliczanie dokładności DLA KAŻDEGO POMIARU
def oblicz_dokladnosc(row):
    if row['algo'] == 'brute_force':
        return 100.0
    koszt_optymalny = optymalne_koszty.get(row['n'])
    if koszt_optymalny and row['cost'] > 0:
        return (koszt_optymalny / row['cost']) * 100
    return None


df['accuracy'] = df.apply(oblicz_dokladnosc, axis=1)

# 3. Uśrednianie wyników podstawowych
df_srednie = df.groupby(['n', 'algo'])[['time', 'accuracy']].mean().reset_index()
df_heur_srednie = df_srednie[(df_srednie['n'] >= 5) & (df_srednie['n'] <= 14)]

# ==========================================
# GENEROWANIE TABEL
# ==========================================
print("Generowanie tabel CSV...")

df_czasy = df_srednie[df_srednie['algo'] != 'rand']
tabela_czasow = df_czasy.pivot(index='n', columns='algo', values='time')
kolumny_dostepne = [col for col in ['nn', 'rnn', 'brute_force'] if col in tabela_czasow.columns]
tabela_czasow = tabela_czasow[kolumny_dostepne]
tabela_czasow.to_csv(f'{FOLDER_WYJSCIOWY}/tabela_czasow.csv', float_format='%.6f')

df_rand = df[df['algo'] == 'rand'].copy()

bins_macro = list(range(0, 65, 5)) + [120, 180, 240, 300]
labels_macro = [f"{i}-{i + 5}s" for i in range(0, 60, 5)] + ["1-2m", "2-3m", "3-4m", "4-5m"]
df_rand['bin_macro'] = pd.cut(df_rand['time'], bins=bins_macro, labels=labels_macro)
tabela_rand_macro = df_rand.groupby(['bin_macro', 'n'])['accuracy'].mean().unstack()
tabela_rand_macro.dropna(how='all', inplace=True)
tabela_rand_macro.to_csv(f'{FOLDER_WYJSCIOWY}/tabela_rand_macro.csv', float_format='%.2f')

bins_micro = list(range(10, 52, 1))
labels_micro = [f"{i}us" for i in range(10, 51)]
df_rand['bin_micro'] = pd.cut(df_rand['time_us'], bins=bins_micro, labels=labels_micro)
tabela_rand_micro = df_rand.groupby(['bin_micro', 'n'])['accuracy'].mean().unstack()
tabela_rand_micro.dropna(how='all', inplace=True)
tabela_rand_micro.to_csv(f'{FOLDER_WYJSCIOWY}/tabela_rand_micro.csv', float_format='%.2f')

# ==========================================
# WYKRESY
# ==========================================
print("Generowanie wykresów...")


# --- Funkcja pomocnicza do rysowania wykresów przedziałowych dla N=14 ---
def rysuj_wykres_n14(dane, tytul, plik_baza, x_kolumna, x_etykieta, x_log=False):
    plt.figure(figsize=(10, 6))
    plt.scatter(dane[x_kolumna], dane['accuracy'],
                label='RAND N=14 (Pojedyncze pomiary)',
                color='orange', s=50, alpha=0.5, edgecolors='none')

    plt.title(tytul)
    plt.xlabel(x_etykieta)
    plt.ylabel('Dokładność [%]')
    if x_log:
        plt.xscale('log')
    plt.legend(loc='lower right')
    plt.grid(True, linestyle='--', alpha=0.5, which='both')
    plt.tight_layout()
    plt.savefig(f'{FOLDER_WYJSCIOWY}/{plik_baza}.png')
    plt.savefig(f'{FOLDER_WYJSCIOWY}/{plik_baza}.pdf')
    plt.close()


# WYKRES 1: Brute Force
plt.figure(figsize=(8, 6))
bf_srednie = df_srednie[df_srednie['algo'] == 'brute_force'].sort_values(by='n')
plt.plot(bf_srednie['n'], bf_srednie['time'], marker='o', color='red', linewidth=2)
plt.title('Czas obliczeń Brute Force vs N')
plt.xlabel('Rozmiar instancji (N)')
plt.ylabel('Średni czas obliczeń [s]')
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(f'{FOLDER_WYJSCIOWY}/brute_force_czas_vs_n.png', bbox_inches='tight')
plt.savefig(f'{FOLDER_WYJSCIOWY}/brute_force_czas_vs_n.pdf', bbox_inches='tight')
plt.close()

# ==========================================
# NOWE WYKRESY RAND (TYLKO N=14) W PRZEDZIAŁACH
# ==========================================
df_rand_14 = df_rand[df_rand['n'] == 14]

# A: Całość - skala logarytmiczna
rysuj_wykres_n14(df_rand_14, 'Dokładność RAND N=14 (Całość - Skala Log)',
                 'rand_n14_calosc_log', 'time_ms', 'Czas pomiaru [ms] (Log)', x_log=True)

# B: 10us - 200us (skala normalna)
dane_10_200us = df_rand_14[(df_rand_14['time_us'] >= 10) & (df_rand_14['time_us'] <= 200)]
rysuj_wykres_n14(dane_10_200us, 'Dokładność RAND N=14 (10 µs - 200 µs)',
                 'rand_n14_10us_200us', 'time_us', 'Czas pomiaru [µs]')

# C: 200us - 2000us (skala normalna)
dane_200_2000us = df_rand_14[(df_rand_14['time_us'] >= 200) & (df_rand_14['time_us'] <= 2000)]
rysuj_wykres_n14(dane_200_2000us, 'Dokładność RAND N=14 (200 µs - 2000 µs)',
                 'rand_n14_200us_2000us', 'time_us', 'Czas pomiaru [µs]')

# D: 2ms - 100ms (skala normalna)
dane_2_100ms = df_rand_14[(df_rand_14['time_ms'] >= 2) & (df_rand_14['time_ms'] <= 100)]
rysuj_wykres_n14(dane_2_100ms, 'Dokładność RAND N=14 (2 ms - 100 ms)',
                 'rand_n14_2ms_100ms', 'time_ms', 'Czas pomiaru [ms]')

# E: 1ms - 1s (skala normalna)
dane_1ms_1s = df_rand_14[(df_rand_14['time_ms'] >= 1) & (df_rand_14['time'] <= 1)]
rysuj_wykres_n14(dane_1ms_1s, 'Dokładność RAND N=14 (1 ms - 1 s)',
                 'rand_n14_1ms_1s', 'time_ms', 'Czas pomiaru [ms]')

# ==========================================
# WYKRES 3: NN, RNN i RAND (TYLKO N=14, 10-50 us, SKALA LINIOWA)
# ==========================================
plt.figure(figsize=(10, 6))
algorytmy_deterministyczne = {'nn': 'blue', 'rnn': 'green'}

# 1. Punkty dla NN i RNN (Przeliczamy czas na mikrosekundy dla czytelności skali liniowej)
for algo, kolor in algorytmy_deterministyczne.items():
    dane_algo = df_heur_srednie[df_heur_srednie['algo'] == algo]
    plt.scatter(dane_algo['time'] * 1e6, dane_algo['accuracy'],
                label=algo.upper(), color=kolor, s=100, alpha=0.7, edgecolors='black', zorder=3)
    for _, row in dane_algo.iterrows():
        # Etykiety nad punktami
        plt.annotate(f"{int(row['n'])}", (row['time'] * 1e6, row['accuracy']),
                     textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8)

# 2. RAND - Tylko N=14, zakres 10-50 us, agregacja co 1 us
dane_rand_micro = df_rand_14[(df_rand_14['time_us'] >= 10) & (df_rand_14['time_us'] <= 50)].copy()

if not dane_rand_micro.empty:
    dane_rand_micro['time_us_bin'] = dane_rand_micro['time_us'].astype(int)
    rand_14 = dane_rand_micro.groupby('time_us_bin')['accuracy'].mean().reset_index()

    plt.plot(rand_14['time_us_bin'], rand_14['accuracy'],
             color='orange', label='RAND N=14 (średnia co 1 µs)', linewidth=2.5, zorder=2)

plt.title('Dokładność vs Czas obliczeń (NN, RNN vs RAND dla 10-50 µs)')
plt.xlabel('Czas obliczeń [µs] (Skala Liniowa)')
plt.ylabel('Średnia dokładność [%]')

# Sztywne okno wykresu w skali liniowej od 10 do 50 mikrosekund
plt.xlim(10, 50)

plt.legend(loc='lower right')
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(f'{FOLDER_WYJSCIOWY}/dokladnosc_czas_nn_rnn_rand_liniowa_10_50us.png', bbox_inches='tight')
plt.savefig(f'{FOLDER_WYJSCIOWY}/dokladnosc_czas_nn_rnn_rand_liniowa_10_50us.pdf', bbox_inches='tight')
plt.close()

# WYKRES 4: Czas NN i RNN vs N
plt.figure(figsize=(8, 6))
for algo in ['nn', 'rnn']:
    dane_algo = df_srednie[df_srednie['algo'] == algo].sort_values(by='n')
    plt.plot(dane_algo['n'], dane_algo['time'], marker='s', label=algo.upper(), linewidth=2)
plt.title('Czas obliczeń vs N (NN i RNN)')
plt.xlabel('Rozmiar instancji (N)')
plt.ylabel('Średni czas obliczeń [s]')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(f'{FOLDER_WYJSCIOWY}/czas_nn_rnn_vs_n.png', bbox_inches='tight')
plt.savefig(f'{FOLDER_WYJSCIOWY}/czas_nn_rnn_vs_n.pdf', bbox_inches='tight')
plt.close()

# WYKRES 5: Stabilność RAND Boxplot
plt.figure(figsize=(10, 6))
df_rand_raw_boxplot = df[(df['algo'] == 'rand') & (df['n'] >= 5) & (df['n'] <= 14)]
dane_do_boxplota = [grupa['accuracy'].dropna().values for n, grupa in df_rand_raw_boxplot.groupby('n')]
ns = sorted(df_rand_raw_boxplot['n'].unique())
plt.boxplot(dane_do_boxplota, tick_labels=ns, patch_artist=True,
            boxprops=dict(facecolor='orange', color='black'),
            medianprops=dict(color='red', linewidth=2))
plt.title('Stabilność algorytmu RAND (Rozrzut dokładności w wielu pomiarach)')
plt.xlabel('Rozmiar instancji (N)')
plt.ylabel('Dokładność w pojedynczym pomiarze [%]')
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.savefig(f'{FOLDER_WYJSCIOWY}/stabilnosc_rand.png', bbox_inches='tight')
plt.savefig(f'{FOLDER_WYJSCIOWY}/stabilnosc_rand.pdf', bbox_inches='tight')
plt.close()

print(f"Gotowe! Pliki zapisane w: {FOLDER_WYJSCIOWY}/")