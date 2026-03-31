#!/bin/bash

# 1. Konfiguracja
PROGRAM="../pea_project/build/Desktop_Qt_6_10_0-release/pea_project"
MAX_TIME=10
ALGO_ID=1
REPETITIONS=3
MODE=0
IN_FILE_PATH='./generowane/'


# 2. Obliczanie liczby wątków (Liczba CPU - 2)
CPU_CORES=$(nproc)
THREADS=$((CPU_CORES - 2))
if [ $THREADS -lt 1 ]; then THREADS=1; fi

echo "--- Wykryto rdzeni: $CPU_CORES. Używam wątków: $THREADS ---"

# 3. Przygotowanie listy komend do wykonania
# Tworzymy tymczasowy plik z listą wszystkich wywołań
TEMP_COMMANDS="tasks.tmp"
> "$TEMP_COMMANDS"

for x in {5..13}
do
    FILE="${IN_FILE_PATH}/${x}.atsp"
    if [ -f "$FILE" ]; then
        for i in $(seq 1 $REPETITIONS)
        do
            # Zapisujemy pełną komendę do pliku
            echo "$PROGRAM $MAX_TIME $ALGO_ID $FILE $MODE" >> "$TEMP_COMMANDS"
        done
    else
        echo "Pominiecie: $FILE (brak pliku)"
    fi
done

# 4. Uruchomienie wszystkiego przez xargs
# -P $THREADS : puszcza dokładnie tyle procesów naraz
# -I {} : wstawia linię z pliku w miejsce {}
# --arg-file : czyta zadania z pliku
echo "Startuje procesy... Czekaj na zakończenie."
xargs -P $THREADS -I {} sh -c "{}" < "$TEMP_COMMANDS"

# 5. Sprzątanie
rm "$TEMP_COMMANDS"

echo -e "\n--- Wszystkie testy zakończone! ---"
