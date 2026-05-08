#!/bin/bash


PROGRAM="../program/build/Desktop_Qt_6_10_0-Release/pea_project"
MAX_TIME=1
ALGOS=(6) #DFS
REPETITIONS=1
IN_FILE_PATH='../dane/test_data/'

# Tablica z wybranymi instancjimi atsp do rozwiazania
FILE_ENDS=(
    "br17.atsp"
    {5..39}.atsp
    "ftv33.atsp"
    "ftv35.atsp" 
)

#-----------------------------------------------------------------
# 2. Obliczanie liczby wątków
CPU_CORES=$(nproc)
THREADS=$((CPU_CORES - 2))
[ $THREADS -lt 1 ] && THREADS=1

echo "--- Wykryto rdzeni: $CPU_CORES. Używam wątków: $THREADS ---"
#-----------------------------------------------------------------

# 3. Przygotowanie listy komend
TEMP_COMMANDS="tasks.tmp" 
> "$TEMP_COMMANDS"

# KLUCZOWA ZMIANA: Składnia "${NAZWA[@]}" jest niezbędna do iteracji
for FILE_END in "${FILE_ENDS[@]}"
do
    # Zmienna FILE składa się z bazy i konkretnego elementu z pętli
    FILE="${IN_FILE_PATH}${FILE_END}"
    
    if [ -f "$FILE" ]; then
        for i in $(seq 1 $REPETITIONS)
        do
            for algo in "${ALGOS[@]}" ; do
                echo "$PROGRAM $MAX_TIME $algo $FILE" >> "$TEMP_COMMANDS"
            done
        done
    else
        echo "Pominięcie: $FILE (brak pliku)"
    fi
done

# 4. Uruchomienie
echo "Startuje procesy... Czekaj na zakończenie."
xargs -P $THREADS -I {} sh -c "{}" < "$TEMP_COMMANDS"

# 5. Sprzątanie
rm "$TEMP_COMMANDS"

echo -e "\n--- Wszystkie testy zakończone! ---"
speaker-test -t sine -f 800 -l 1 & sleep 0.5 && kill -9 $! &> /dev/null
