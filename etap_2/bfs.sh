#!/bin/bash

# --- KONFIGURACJA ---
PROGRAM="../program/build/Desktop_Qt_6_10_0-Release/pea_project"
MAX_TIME=1             # Czas w sekundach dla narzędzia timeout
ALGOS=(5 7) 
REPETITIONS=5
IN_FILE_PATH='../dane/test_data/'
MAX_RAM_PERCENT=80
RESULTS_FILE="wyniki.csv"
KILLED_FILE="killed.csv"

FILE_ENDS=(
    "br17.atsp"
    "ftv33.atsp"
    "ftv35.atsp" 
    {5..25}.atsp
)

# Obliczanie limitu RAM w KB dla ulimit
TOTAL_RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
MEM_LIMIT_KB=$(( TOTAL_RAM_KB * MAX_RAM_PERCENT / 100 ))

get_algo_name() {
    case $1 in
        5) echo "breadth_first_search" ;;
        7) echo "best_first_search" ;;
        *) echo "unknown_algo" ;;
    esac
}

# --- START TESTÓW ---
echo "Limit RAM ustawiony na: $((MEM_LIMIT_KB / 1024)) MB"

for FILE_END in "${FILE_ENDS[@]}"
do
    FILE="${IN_FILE_PATH}${FILE_END}"
    [ ! -f "$FILE" ] && continue

    BASENAME=$(basename "$FILE_END" .atsp)

    for algo in "${ALGOS[@]}"; do
        ALGO_NAME=$(get_algo_name $algo)
        
        for i in $(seq 1 $REPETITIONS); do
            echo "Test: $BASENAME | Algo: $ALGO_NAME | Próba: $i"

            # Uruchomienie w podpowłoce, aby ulimit dotyczył tylko programu
            (
                ulimit -v $MEM_LIMIT_KB
                # timeout zabije proces po czasie, taskset przypnie do rdzenia 0
                timeout --signal=SIGTERM "${MAX_TIME}s" taskset -c 0 $PROGRAM $MAX_TIME $algo "$FILE"
            )
            
            EXIT_STATUS=$?

            # Interpretacja kodów wyjścia:
            # 124 - timeout zabił proces
            # 137 - proces zabity sygnałem 9 (np. przez system/ulimit przy braku pamięci)
            # 139 - Segmentation fault (często wynik ulimit przy alokacji pamięci)
            if [ $EXIT_STATUS -eq 124 ] || [ $EXIT_STATUS -eq 137 ] || [ $EXIT_STATUS -eq 139 ]; then
                TIMESTAMP=$(date +"%H:%M %d-%m-%Y")
                CAUSE="UNKNOWN/MEMORY"
                [ $EXIT_STATUS -eq 124 ] && CAUSE="TIMEOUT"
                
                echo "${BASENAME};0;${algo};${ALGO_NAME};-5;${TIMESTAMP}" >> "$KILLED_FILE"
                echo "ZABITO/BŁĄD: $BASENAME ($CAUSE). Status: $EXIT_STATUS"
            else
                echo "Zakończono poprawnie: $BASENAME"
            fi

            # Krótka przerwa na ustabilizowanie systemu
            sleep 2
        done
    done
done

echo -e "\n--- Koniec testów ---"