#ifndef ALGORITHMRUNNER_H
#define ALGORITHMRUNNER_H

#include <iostream>
#include <atomic>
#include <chrono>
#include <future>
#include <iostream>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <pthread.h>
#include <time.h>


// ======================================================================
// Klasa Zarządzająca uruchamianiem wątków
// ======================================================================
class AlgorithmRunner {
public:
    template <typename Callable, typename... Args>
    static void run_with_wall_timeout(std::chrono::milliseconds wall_timeout, Callable&& algorithm, Args&&... args) {

        // Narzędzia do usypiania wątku głównego (zastępują future.wait_for)
        std::mutex mtx;
        std::condition_variable cv;
        bool is_finished = false;

        double final_cpu_time = 0.0;
        auto start_wall_time = std::chrono::steady_clock::now();

        // 1. Odpalamy jthread.
        // Zauważ, że jthread samo wstrzykuje 'std::stop_token' jako pierwszy argument!
        std::jthread worker([&](std::stop_token stoken) {

            double start_cpu_time = get_current_thread_cpu_time_in_s();

            // Wywołujemy algorytm, przekazując stop_token
            algorithm(stoken, std::forward<Args>(args)...);

            double end_cpu_time = get_current_thread_cpu_time_in_s();
            final_cpu_time = end_cpu_time - start_cpu_time;

            // 2. Sygnalizujemy Strażnikowi, że skończyliśmy pracę
            {
                std::lock_guard<std::mutex> lock(mtx);
                is_finished = true;
            }
            cv.notify_one(); // Dzwonimy do drzwi Strażnika!
        });

        // --- WĄTEK GŁÓWNY (STRAŻNIK) ---
        std::unique_lock<std::mutex> lock(mtx);

        // cv.wait_for usypia główny wątek. Budzi się gdy minie czas,
        // LUB gdy algorytm sam zawoła cv.notify_one()
        bool completed_in_time = cv.wait_for(lock, wall_timeout, [&] { return is_finished; });

        if (!completed_in_time) {
            std::cout << "[Runner] Minal limit czasu sciennego! Wysylam sygnal STOP...\n";
            // 3. Magia C++20: Wbudowane przerwanie wątku!
            worker.request_stop();
        } else {
            std::cout << "[Runner] Algorytm zakonczyl sie sam przed czasem.\n";
        }

        lock.unlock(); // Zdejmujemy zamek

        // 4. Choć jthread robi to sam w destruktorze, my wywołujemy to ręcznie,
        // aby poczekać aż wątek bezpiecznie zapisze wynik 'final_cpu_time'
        // zanim przejdziemy do wypisywania go na ekran.
        worker.join();

        auto end_wall_time = std::chrono::steady_clock::now();
        std::chrono::duration<double> total_wall = end_wall_time - start_wall_time;

        std::cout << "--------------------------------------------------\n";
        std::cout << "Czas scienny: " << total_wall.count() << " s\n";
        std::cout << "Czas CPU:     " << final_cpu_time << " s\n";
        std::cout << "--------------------------------------------------\n";
    }
//=================================================================================================================
private :
        double final_cpu_time;
//=================================================================================================================
private:
    static double get_current_thread_cpu_time_in_s() {
        clockid_t cid;
        // pthread_self() bierze ID wątku, który właśnie wywołuje tę funkcję
        if (pthread_getcpuclockid(pthread_self(), &cid) == 0) {
            struct timespec ts;
            if (clock_gettime(cid, &ts) == 0) {
                return ts.tv_sec + ts.tv_nsec * 1e-9;
            }
        }
        return 0.0;
    }
};

#endif // ALGORITHMRUNNER_H




