#ifndef WEKTOR_H
#define WEKTOR_H

#include <initializer_list>
using T = int;
class Wektor
{
public:
    Wektor(std::initializer_list<T> list);
    Wektor(std::size_t init_size);
    Wektor() = delete;

    Wektor(const Wektor & org) noexcept;
    Wektor(Wektor && org) noexcept;
    Wektor & operator=(const Wektor & org);
    Wektor & operator=(Wektor && org);

    ~Wektor();
public:
    T & operator[](std::size_t idx);
    bool push_back(const T &elem);
public:
    void copy(const Wektor & org);
    void move(Wektor && org);
    void grow();
private:
    std::size_t growPolicy();
private:
    static constexpr double growFactor = 2;
    std::size_t size = 0;
    std::size_t capacity = 0;
    T * data_ptr = nullptr;

};

#endif // WEKTOR_H
