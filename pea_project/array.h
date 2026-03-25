#ifndef ARRAY_H
#define ARRAY_H



#include <cstddef>

//todo zastanowic sie nad stalymi macierzami
namespace pea{
using T = int;

class Array
{
public:
    Array(std::size_t n);
    ~Array();
    Array(const Array & org) = delete;    //nie ma kopiowania
    Array(Array && org);
public:
    Array & operator=(const Array &org);
    Array & operator=(Array && org);
public:
    const T get(std::size_t row, std::size_t col);
    void set(T value, std::size_t row, std::size_t col);
    const std::size_t getSize();
    T* operator[](std::size_t row);


private:
    T* data_ptr = nullptr;    //zle sie czuje z faktem uzycia raw pointers
    std::size_t size;
};
}//end of namespace pea
#endif // ARRAY_H
