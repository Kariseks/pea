#ifndef ALGORITHMRUNNER_H
#define ALGORITHMRUNNER_H

#include <chrono>
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
    void run_with_wall_timeout(std::chrono::seconds wall_timeout, Callable&& algorithm, Args&&... args) {

        std::mutex mtx;
        std::condition_variable cv;
        bool is_finished = false;

        auto start_wall_time = std::chrono::steady_clock::now();

        // 1. Odpalamy jthread.
        std::jthread worker([&](std::stop_token stoken) {

            double start_cpu_time = get_current_thread_cpu_time_in_s();

            // Wywołujemy algorytm, przekazując stop_token
            algorithm(stoken, std::forward<Args>(args)...);

            final_cpu_time_in_s = get_current_thread_cpu_time_in_s() - start_cpu_time;

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
        completed_in_time = cv.wait_for(lock, wall_timeout, [&] { return is_finished; });
        if (!completed_in_time) {

            worker.request_stop();
        }
        lock.unlock();

        worker.join();

        //auto end_wall_time = std::chrono::steady_clock::now();
        //std::chrono::duration<double> total_wall = end_wall_time - start_wall_time;


    }
//=================================================================================================================
    double getFinal_cpu_time_in_s() const;

    bool getCompleted_in_time_in_s() const;

private :
    double final_cpu_time_in_s;
    bool completed_in_time = false;
//=================================================================================================================
public:
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




