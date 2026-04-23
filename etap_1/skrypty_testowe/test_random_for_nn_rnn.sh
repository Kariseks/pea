#!/bin/bash

# 1. Konfiguracja - Tablica MUSI być zdefiniowana w nawiasach, elementy oddzielone spacją
PROGRAM="../pea_project/build/Desktop_Qt_6_10_0-release/pea_project"
MAX_TIME=1
ALGOS=(2 )
REPETITIONS=50
MODE=0
IN_FILE_PATH='./test_data/'

# Poprawiona definicja tablicy
FILE_ENDS=(
    "5.atsp" "6.atsp" "7.atsp" "8.atsp" "9.atsp" "10.atsp" "11.atsp" "12.atsp" "13.atsp" "14.atsp"	
    "br17.atsp" "ftv33.atsp" "ftv47.atsp" "kro124p.atsp" "rbg403.atsp"
    "ft53.atsp" "ftv35.atsp" "ftv55.atsp" "p43.atsp" "rbg443.atsp"
    "ft70.atsp" "ftv38.atsp" "ftv64.atsp" "rbg323.atsp" 
    "ftv170.atsp" "ftv44.atsp" "ftv70.atsp" "rbg358.atsp"
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
                echo "$PROGRAM $MAX_TIME $algo $FILE $MODE" >> "$TEMP_COMMANDS"
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
