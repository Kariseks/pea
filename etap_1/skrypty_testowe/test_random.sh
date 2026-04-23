#!/bin/bash

# 1. Konfiguracja
PROGRAM="../pea_project/build/Desktop_Qt_6_10_0-release/pea_project"
MIN_TIME=1          # NOWE: Minimalny czas w sekundach
MAX_TIME=60          # ZMIANA: Maksymalny czas (ustaw na ile potrzebujesz)
KROK=5
ALGO_ID=2
REPETITIONS=10
MODE=0
file="./test_data/rbg358.atsp"


# 2. Obliczanie liczby wątków (Liczba CPU - 2)
CPU_CORES=$(nproc)
THREADS=$((CPU_CORES - 2))
if [ $THREADS -lt 1 ]; then THREADS=1; fi

echo "--- Wykryto rdzeni: $CPU_CORES. Używam wątków: $THREADS ---"

# 3. Przygotowanie listy komend do wykonania
# Tworzymy tymczasowy plik z listą wszystkich wywołań
TEMP_COMMANDS="tasks.tmp"
> "$TEMP_COMMANDS"



if [ -f "$file" ]; then
    # NOWE: Pętla iterująca po czasie od MIN_TIME do MAX_TIME (domyślnie krok to 1)
    for CURRENT_TIME in $(seq $MIN_TIME $KROK $MAX_TIME)
    do
        for i in $(seq 1 $REPETITIONS)
        do
            # Zapisujemy pełną komendę do pliku, używając zmiennej $CURRENT_TIME
            echo "$PROGRAM $CURRENT_TIME $ALGO_ID $file $MODE" >> "$TEMP_COMMANDS"
        done
    done
else
    echo "Pominiecie: $file (brak pliku)"
fi


# 4. Uruchomienie wszystkiego przez xargs
# -P $THREADS : puszcza dokładnie tyle procesów naraz
# -I {} : wstawia linię z pliku w miejsce {}
echo "Startuje procesy... Czekaj na zakończenie."
xargs -P $THREADS -I {} sh -c "{}" < "$TEMP_COMMANDS"

# 5. Sprzątanie
rm "$TEMP_COMMANDS"

echo -e "\n--- Wszystkie testy zakończone! ---"
speaker-test -t sine -f 800 -l 1 & sleep 0.5 && kill -9 $! >> /dev/null
