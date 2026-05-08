#ifndef ARRAY_H
#define ARRAY_H



#include <cstddef>

#include "config.h"
//todo zastanowic sie nad stalymi macierzami
namespace pea{

class Array
{
public:
    Array(const std::size_t n);
    ~Array();
    Array(const Array & org);
    Array(Array && org) noexcept;
public:
    Array & operator=(const Array &org);
    Array & operator=(Array && org);
public:
     T get(std::size_t row, std::size_t col) const;
    void set(T value, std::size_t row, std::size_t col);
    const std::size_t getSize() const;
    T* operator[](std::size_t row);


private:
    T* data_ptr = nullptr;    //zle sie czuje z faktem uzycia raw pointers, ale czego sie nie robi dal wydajnosci
    std::size_t size;
};
}//end of namespace pea
#endif // ARRAY_H
