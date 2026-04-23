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
optimum_costs = {
    5: 205,
    6: 150,
    7: 147,
    8: 149,
    9: 140,
    10: 102,
    11: 129,
    12: 176,
    13: 203,
    14: 133,     #generowane
    17: 39,      # br17
    53: 6905,    # ft53
    70: 38673,   # ft70
    34: 1286,    # ftv33
    36: 1473,    # ftv35
    39: 1530,    # ftv38
    45: 1613,    # ftv44
    48: 1776,    # ftv47
    56: 1608,    # ftv55
    65: 1839,    # ftv64
    71: 1950,    # ftv70
    91: 1579,    # ftv90
    101: 1788,   # ftv100
    111: 1958,   # ftv110
    121: 2166,   # ftv120
    131: 2307,   # ftv130
    141: 2420,   # ftv140
    151: 2611,   # ftv150
    161: 2683,   # ftv160
    171: 2755,   # ftv170
    100: 36230,  # kro124
    43: 5620,    # p43
    323: 1326,   # rbg323
    358: 1163,   # rbg358
    403: 2465,   # rbg403
    443: 2720,   # rbg443
}

# Tworzenie folderu wyjściowego, jeśli nie istnieje
os.makedirs(FOLDER_WYJSCIOWY, exist_ok=True)

print("Wczytywanie i przetwarzanie danych...")
kolumny = ['time', 'n', 'algo', 'cost', 'timestamp']
results = pd.read_csv(PLIK_WYNIKOW, sep=';', names=kolumny, usecols=kolumny[0:4]) #bez timestamps

# Wymuszenie typu całkowitego dla 'n'
results['n'] = pd.to_numeric(results['n'], errors='coerce').fillna(0).astype(int)




# ==========================================
# Przetwarzenie wynikow
# ==========================================

# 2. Obliczanie błędu względnego DLA KAŻDEGO POMIARU
def oblicz_blad_wzgledny(row_in):

    n = int(row_in['n'])

    # Bezpieczne rzutowanie kosztu na float
    try:
        koszt_aktualny = float(row_in['cost'])
        koszt_optymalny = float(optimum_costs[n])
    except (ValueError, TypeError):
        raise ValueError(f"Błąd: konwersji n={n}!")
    except KeyError:
        raise ValueError(f"Błąd: Brak zdefiniowanego optimum dla n={n}!")


    if koszt_optymalny > 0:
        return (abs(koszt_aktualny - koszt_optymalny) / koszt_optymalny) * 100.0 #blad wzgledny
        #return (abs(koszt_aktualny - koszt_optymalny) / koszt_optymalny) * 100.0
        #return (koszt_optymalny / koszt_aktualny) * 100    #quality ratio

    raise ValueError(f"Błąd: cala funkcja n={n}!")

# 3. Uśrednianie wyników podstawowych
results_mean = results[results['algo'] != 'random'].groupby(['n', 'algo'])[['time', 'cost']].mean().reset_index()
#wyciagniecie rand osobno, wazny jest rozrzut, czyli potrzewbna jest kazda instancja, nie mozna usredniac
results_rand = results[results['algo'] == 'random'].copy()
# Dodanie kolumny z bledem wzglendym
results_mean['rel_error'] = results_mean.apply(oblicz_blad_wzgledny, axis=1) #axis=1 oznacza przejscie po wierszach
results_rand['rel_error'] = results_rand.apply(oblicz_blad_wzgledny, axis=1) #axis=1 oznacza przejscie po wierszach

# Obliczanie czasu w różnych jednostkach
results_mean['time_ns'] = results_mean['time'] * 1e9
results_mean['time_us'] = results_mean['time'] * 1e6
results_mean['time_ms'] = results_mean['time'] * 1e3
results_mean['time_min'] = results_mean['time'] / 60.0

results_rand['time_ns'] = results_rand['time'] * 1e9
results_rand['time_us'] = results_rand['time'] * 1e6
results_rand['time_ms'] = results_rand['time'] * 1e3
results_rand['time_min'] = results_rand['time'] / 60.0




# ==========================================
# GENEROWANIE TABEL
# ==========================================
print("Generowanie tabel CSV...")

number_format = '%.4f'

# 1. srednie czasy brute force
df_bruteForce_time = results_mean[results_mean['algo'] == 'brute_force'].copy()
df_bruteForce_time=df_bruteForce_time.sort_values(by='n')
df_bruteForce_time.to_csv(f'{FOLDER_WYJSCIOWY}/bruteForce_time.csv',
               sep=';',
               index=False,
               columns=['n', 'time'],
               header=['N', 'średniCzas[s]'],
               #float_format=number_format
                          )

# 2.sredni czas + blad NN i RNN
df_nn_rnn = results_mean[results_mean['algo'].isin(['nn', 'rnn'])].copy()
df_pivot = df_nn_rnn.pivot(index='n', columns='algo', values=['time', 'rel_error'])

# Splaszczenie kolumn (powstaną: 'time_nn', 'time_rnn', 'rel_error_nn', 'rel_error_rnn')
df_pivot.columns = [f'{val}_{algo}' for val, algo in df_pivot.columns]
df_pivot.reset_index(inplace=True)

# Poprawiony zapis do CSV - nowe nazwy kolumn i 5 nagłówków
df_pivot.to_csv(f'{FOLDER_WYJSCIOWY}/nn_rnn_time.csv',
               sep=';',
               index=False,
               columns=['n', 'rel_error_nn', 'rel_error_rnn', 'time_nn', 'time_rnn'],
               header=['N', 'błądNN', 'błądRNN', 'czasNNs', 'czasRNNs'],
               #float_format=number_format
                )
#-----------------------------------------------------------------------------------------------------------------------
#3 random i jego dane

df_n14 = results_rand[(results_rand['n'] == 14) & (results_rand['algo'] == 'random')].copy()

import pandas as pd
import numpy as np


# Funkcja pomocnicza, aby nie powtarzać kodu dla każdej jednostki
def agreguj_koszyki(df, col_bin, jednostka):
    # Grupowanie i agregacja
    stats = df.groupby(col_bin, observed=True)['rel_error'].agg([
        'mean', 'max', 'min', 'var', 'count'
    ]).reset_index()

    # Zmiana nazw i dodanie metadanych
    stats.columns = ['przedzial', 'sredni_blad', 'max_blad', 'min_blad', 'wariancja', 'liczba_probek']
    stats['jednostka'] = jednostka
    stats['przedzial'] = stats['przedzial'].astype(str)

    # Reorganizacja kolumn: jednostka na początku
    return stats[['jednostka', 'przedzial', 'sredni_blad', 'max_blad', 'min_blad', 'wariancja', 'liczba_probek']]


# 1. Obliczamy bins (Twoje definicje)
df_n14['bin_s'] = pd.cut(df_n14['time'], bins=np.arange(0, 61, 5))
df_n14['bin_ms'] = pd.cut(df_n14['time_ms'], bins=np.arange(0, 1001, 50))
df_n14['bin_us'] = pd.cut(df_n14['time_us'], bins=np.arange(0, 1001, 50))

# 2. Generujemy pod-tabele dla każdej jednostki
stats_s = agreguj_koszyki(df_n14, 'bin_s', 's')
stats_ms = agreguj_koszyki(df_n14, 'bin_ms', 'ms')
stats_us = agreguj_koszyki(df_n14, 'bin_us', 'us')

# 3. Łączymy wszystko w jedną tabelę "koszyczki"
koszyczki = pd.concat([stats_s, stats_ms, stats_us], ignore_index=True)

# 4. Eksport
koszyczki.to_csv(f'{FOLDER_WYJSCIOWY}/analiza_koszykowa_rand.csv',
                 sep=';',
                 index=False,
                 columns=['jednostka', 'przedzial', 'sredni_blad', 'max_blad', 'min_blad', 'wariancja', 'liczba_probek'],
                 header=['jednostka', 'przedzial', 'sredniBlad', 'maxBlad', 'minBlad', 'wariancja', 'liczbaProbek'],
                 float_format=number_format)
#-----------------------------------------------------------------------------------------------------------------------






# ======================================================================================================================
# WYKRESY
# ======================================================================================================================
print("Generowanie wykresów...")

# WYKRES 1: Brute Force
df_bruteForce_time

plt.plot(df_bruteForce_time['n'], df_bruteForce_time['time'], marker='o', color='red', linewidth=2)
plt.title('Czas obliczeń Brute Force w funkcji wielkości instancji')
plt.xlabel('Rozmiar instancji (N)')
plt.ylabel('Średni czas obliczeń [s]')
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(f'{FOLDER_WYJSCIOWY}/brute_force.pdf', bbox_inches='tight')
plt.close()

# ===========================================================================================
# WYKRES: Czas NN i RNN vs N
# Ustawienie jednostki (mikrosekundy)
#us
#jedn = 1e6
#jedn_sym = '[\u03BCs]'
#ms
jedn = 1e3
jedn_sym = 'ms'

df_nn_rnn_wykr = results_mean[results_mean['algo'].isin(['nn', 'rnn'])].copy()
df_nn_rnn_wykr = df_nn_rnn_wykr.sort_values(by='n')

plt.figure(figsize=(8, 6))
for algo in ['nn', 'rnn']:
    dane_algo = df_nn_rnn_wykr[df_nn_rnn_wykr['algo'] == algo]
    plt.plot(dane_algo['n'], dane_algo['time'] * jedn, marker='s', label=algo.upper(), linewidth=2)

plt.title('Czas obliczeń dla NN i RNN w funkcji wielkości instancji')
plt.xlabel('Rozmiar instancji (N)')
plt.ylabel(f'Średni czas obliczeń {jedn_sym}')  # \u03BC to symbol mikro (μ)

plt.yscale('log') #dla skali logarytmicznej

plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(f'{FOLDER_WYJSCIOWY}/czas_nn_rnn_vs_n.pdf', bbox_inches='tight')
plt.close()


# ===========================================================================================
#Wykres slupkowy rand: dokladnosc vs czas
# 1. Sprawdź dokładnie nazwę: 'rand' czy 'random'?
# Dodatkowo upewniamy się, że rel_error jest liczbą.
slupki_rand = results_rand[(results_rand['n'] == 14) &
                           (results_rand['algo'].isin(['rand', 'random']))].copy()

# Konwersja na float na wszelki wypadek, by uniknąć błędów w obliczeniach
slupki_rand['rel_error'] = pd.to_numeric(slupki_rand['rel_error'], errors='coerce')
slupki_rand['time'] = pd.to_numeric(slupki_rand['time'], errors='coerce')

# 2. Grupowanie
slupki_rand['przedzial'] = pd.cut(slupki_rand['time'], bins=np.arange(1, 67, 5))

# 3. Agregacja
statystyki_rand = slupki_rand.groupby('przedzial', observed=True)['rel_error'].agg([
    'mean', 'min', 'max', 'count']).reset_index()

# Usuwamy puste i upewniamy się, że mamy poprawne liczby
statystyki_rand = statystyki_rand[statystyki_rand['count'] > 0].copy()

# 4. Rysowanie wykresu punktowego z wąsami (Errorbar)
plt.figure(figsize=(12, 6))

# Obliczanie wąsów z zabezpieczeniem przed zerem (clip)
dolne_wasy = (statystyki_rand['mean'] - statystyki_rand['min']).clip(lower=0)
gorne_wasy = (statystyki_rand['max'] - statystyki_rand['mean']).clip(lower=0)
yerr = [dolne_wasy, gorne_wasy]

# ZAMIAST plt.bar UŻYWAMY plt.errorbar
plt.errorbar(x=statystyki_rand['przedzial'].astype(str),
             y=statystyki_rand['mean'],
             yerr=yerr,
             fmt='o',              # 'o' oznacza kropkę (znacznik średniej). Możesz zmienić na '_' (pozioma kreska)
             color='firebrick',    # Kolor znacznika (średniej)
             ecolor='black',       # Kolor wąsów (min-max)
             capsize=5,            # Wielkość poprzecznych kresek na końcach wąsów
             capthick=1.5,         # Grubość poprzecznych kresek
             elinewidth=1.5,       # Grubość pionowej linii rozrzutu
             markersize=8,         # Wielkość kropki
             linestyle='--',       # '--' łączy średnie przerywaną linią (pokazuje trend). Jeśli nie chcesz linii, wpisz 'None'
             alpha=0.8)

# Formatowanie osi i tytułów
plt.xticks(rotation=45, ha='right')
plt.xlabel('Przedziały czasowe [s]')
plt.ylabel('Błąd względny [%]')
plt.title('Średni błąd względny algorytmu RAND w czasie z rozrzutem Min-Max (N=14)')
plt.grid(axis='y', linestyle=':', alpha=0.7)

# Wymuszenie początku osi Y od zera, aby wykres "nie wisiał" w powietrzu
#plt.ylim(bottom=0)

plt.tight_layout()
plt.savefig(f'{FOLDER_WYJSCIOWY}/rand_errorbar_rozrzut.pdf') # Zmieniłem nazwę pliku, żeby nie nadpisać starego
plt.close()

# ===========================================================================================
#Wykres slupkowy rand: dokladnosc vs czas 47
# 1. Sprawdź dokładnie nazwę: 'rand' czy 'random'?
# Dodatkowo upewniamy się, że rel_error jest liczbą.
slupki_rand = results_rand[(results_rand['n'] == 48) &
                           (results_rand['algo'].isin(['rand', 'random']))].copy()

# Konwersja na float na wszelki wypadek, by uniknąć błędów w obliczeniach
slupki_rand['rel_error'] = pd.to_numeric(slupki_rand['rel_error'], errors='coerce')
slupki_rand['time'] = pd.to_numeric(slupki_rand['time'], errors='coerce')

# 2. Grupowanie
slupki_rand['przedzial'] = pd.cut(slupki_rand['time'], bins=np.arange(1, 67, 5))

# 3. Agregacja
statystyki_rand = slupki_rand.groupby('przedzial', observed=True)['rel_error'].agg([
    'mean', 'min', 'max', 'count']).reset_index()

# Usuwamy puste i upewniamy się, że mamy poprawne liczby
statystyki_rand = statystyki_rand[statystyki_rand['count'] > 0].copy()

# 4. Rysowanie wykresu punktowego z wąsami (Errorbar)
plt.figure(figsize=(12, 6))

# Obliczanie wąsów z zabezpieczeniem przed zerem (clip)
dolne_wasy = (statystyki_rand['mean'] - statystyki_rand['min']).clip(lower=0)
gorne_wasy = (statystyki_rand['max'] - statystyki_rand['mean']).clip(lower=0)
yerr = [dolne_wasy, gorne_wasy]

# ZAMIAST plt.bar UŻYWAMY plt.errorbar
plt.errorbar(x=statystyki_rand['przedzial'].astype(str),
             y=statystyki_rand['mean'],
             yerr=yerr,
             fmt='o',              # 'o' oznacza kropkę (znacznik średniej). Możesz zmienić na '_' (pozioma kreska)
             color='firebrick',    # Kolor znacznika (średniej)
             ecolor='black',       # Kolor wąsów (min-max)
             capsize=5,            # Wielkość poprzecznych kresek na końcach wąsów
             capthick=1.5,         # Grubość poprzecznych kresek
             elinewidth=1.5,       # Grubość pionowej linii rozrzutu
             markersize=8,         # Wielkość kropki
             linestyle='--',       # '--' łączy średnie przerywaną linią (pokazuje trend). Jeśli nie chcesz linii, wpisz 'None'
             alpha=0.8)

# Formatowanie osi i tytułów
plt.xticks(rotation=45, ha='right')
plt.xlabel('Przedziały czasowe [s]')
plt.ylabel('Błąd względny [%]')
plt.title('Średni błąd względny algorytmu RAND w czasie z rozrzutem Min-Max (N=48)')
plt.grid(axis='y', linestyle=':', alpha=0.7)

# Wymuszenie początku osi Y od zera, aby wykres "nie wisiał" w powietrzu
#plt.ylim(bottom=0)

plt.tight_layout()
plt.savefig(f'{FOLDER_WYJSCIOWY}/rand_errorbar_rozrzut_47.pdf') # Zmieniłem nazwę pliku, żeby nie nadpisać starego
plt.close()
# ===========================================================================================
#Wykres slupkowy rand: dokladnosc vs czas 358
# 1. Sprawdź dokładnie nazwę: 'rand' czy 'random'?
# Dodatkowo upewniamy się, że rel_error jest liczbą.
slupki_rand = results_rand[(results_rand['n'] == 358) &
                           (results_rand['algo'].isin(['rand', 'random']))].copy()

# Konwersja na float na wszelki wypadek, by uniknąć błędów w obliczeniach
slupki_rand['rel_error'] = pd.to_numeric(slupki_rand['rel_error'], errors='coerce')
slupki_rand['time'] = pd.to_numeric(slupki_rand['time'], errors='coerce')

# 2. Grupowanie
slupki_rand['przedzial'] = pd.cut(slupki_rand['time'], bins=np.arange(1, 67, 5))

# 3. Agregacja
statystyki_rand = slupki_rand.groupby('przedzial', observed=True)['rel_error'].agg([
    'mean', 'min', 'max', 'count']).reset_index()

# Usuwamy puste i upewniamy się, że mamy poprawne liczby
statystyki_rand = statystyki_rand[statystyki_rand['count'] > 0].copy()

# 4. Rysowanie wykresu punktowego z wąsami (Errorbar)
plt.figure(figsize=(12, 6))

# Obliczanie wąsów z zabezpieczeniem przed zerem (clip)
dolne_wasy = (statystyki_rand['mean'] - statystyki_rand['min']).clip(lower=0)
gorne_wasy = (statystyki_rand['max'] - statystyki_rand['mean']).clip(lower=0)
yerr = [dolne_wasy, gorne_wasy]

# ZAMIAST plt.bar UŻYWAMY plt.errorbar
plt.errorbar(x=statystyki_rand['przedzial'].astype(str),
             y=statystyki_rand['mean'],
             yerr=yerr,
             fmt='o',              # 'o' oznacza kropkę (znacznik średniej). Możesz zmienić na '_' (pozioma kreska)
             color='firebrick',    # Kolor znacznika (średniej)
             ecolor='black',       # Kolor wąsów (min-max)
             capsize=5,            # Wielkość poprzecznych kresek na końcach wąsów
             capthick=1.5,         # Grubość poprzecznych kresek
             elinewidth=1.5,       # Grubość pionowej linii rozrzutu
             markersize=8,         # Wielkość kropki
             linestyle='--',       # '--' łączy średnie przerywaną linią (pokazuje trend). Jeśli nie chcesz linii, wpisz 'None'
             alpha=0.8)

# Formatowanie osi i tytułów
plt.xticks(rotation=45, ha='right')
plt.xlabel('Przedziały czasowe [s]')
plt.ylabel('Błąd względny [%]')
plt.title('Średni błąd względny algorytmu RAND w czasie z rozrzutem Min-Max (N=358)')
plt.grid(axis='y', linestyle=':', alpha=0.7)

# Wymuszenie początku osi Y od zera, aby wykres "nie wisiał" w powietrzu
#plt.ylim(bottom=0)

plt.tight_layout()
plt.savefig(f'{FOLDER_WYJSCIOWY}/rand_errorbar_rozrzut_358.pdf') # Zmieniłem nazwę pliku, żeby nie nadpisać starego
plt.close()

# ===========================================================================================
#Wykres dokladnosc nn i rnn w funkcji czasu, srednia dla radn
# ===========================================================================================
# Wykres błędu dla NN i RNN w funkcji wielkości instancji (N)
# ===========================================================================================
print("Rysowanie wykresu błędu NN i RNN...")

# Przygotowanie i posortowanie danych
df_nn_rnn_blad = results_mean[results_mean['algo'].isin(['nn', 'rnn'])].copy()
df_nn_rnn_blad = df_nn_rnn_blad.sort_values(by='n')

plt.figure(figsize=(10, 6))

# Rysowanie linii dla każdego algorytmu
for algo in ['nn', 'rnn']:
    dane_algo = df_nn_rnn_blad[df_nn_rnn_blad['algo'] == algo]

    # Różne kolory/kształty punktów przypisane z automatu przez plt.plot
    plt.plot(dane_algo['n'], dane_algo['rel_error'],
             marker='o',
             label=algo.upper(),
             linewidth=2)

# Formatowanie wykresu
plt.title('Błąd względny NN i RNN w funkcji wielkości instancji')
plt.xlabel('Rozmiar instancji (N)')
plt.ylabel('Błąd względny [%]')

plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)

# Zapis do pliku
plt.tight_layout()
plt.savefig(f'{FOLDER_WYJSCIOWY}/blad_nn_rnn_vs_n.pdf', bbox_inches='tight')
plt.close()

print("Gotowe! Wszystkie skrypty wykonane pomyślnie.")


# ===========================================================================================v
# ===========================================================================================
# WYKRES: Błąd względny NN, RNN i RANDOM (wykonywany w czasie ~1s) w funkcji N
# ===========================================================================================
print("Rysowanie połączonego wykresu błędu NN, RNN i RAND (~1s)...")

plt.figure(figsize=(10, 6))

# 1. Rysowanie linii dla NN i RNN (korzystamy z przygotowanej wcześniej ramki df_nn_rnn_blad)
for algo in ['nn', 'rnn']:
    dane_algo = df_nn_rnn_blad[df_nn_rnn_blad['algo'] == algo]
    plt.plot(dane_algo['n'], dane_algo['rel_error'],
             marker='o', label=algo.upper(), linewidth=2)

# 2. Przygotowanie danych dla RANDOM (tylko czas między 0.95s a 1.05s)
# Filtrujemy czasy
rand_około_1s = results_rand[(results_rand['time'] >= 0.98) & (results_rand['time'] <= 1.02)]

# Grupujemy po 'n', aby policzyć średni błąd względny dla każdej instancji (dla wybranego czasu)
rand_1s_mean = rand_około_1s.groupby('n', observed=True)['rel_error'].mean().reset_index()
# 3. Rysowanie linii dla RANDOM (jeśli znalazły się jakiekolwiek dane w tym przedziale)
if not rand_1s_mean.empty:
    plt.plot(rand_1s_mean['n'], rand_1s_mean['rel_error'],
             marker='^', linestyle='--', color='green', label='RANDOM (~1s)', linewidth=2)
else:
    print("Ostrzeżenie: Brak próbek dla algorytmu random w przedziale czasowym [0.95s, 1.05s]!")

# 4. Formatowanie wykresu
plt.title('Błąd względny NN, RNN oraz RANDOM (~1s) w funkcji wielkości instancji')
plt.xlabel('Rozmiar instancji (N)')
plt.ylabel('Średni błąd względny [%]')

plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)

# Zapis do pliku
plt.tight_layout()
plt.savefig(f'{FOLDER_WYJSCIOWY}/blad_nn_rnn_rand1s_vs_n.pdf', bbox_inches='tight')
plt.close()