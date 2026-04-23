#include "array.h"
#include <algorithm>

using namespace pea;
using namespace std;

Array::Array(const std::size_t n):
    size{n},
    data_ptr{new T[n*n]}
{

}

Array::~Array()
{
    if(data_ptr){
        delete[] data_ptr;
        data_ptr = nullptr;
    }
}

Array::Array(const Array & org)
{
    size = org.size;
    auto elem_n = size*size;
    data_ptr = new T[elem_n];

    std::copy(org.data_ptr, org.data_ptr + (elem_n), data_ptr);
}

Array::Array(Array && org) noexcept
{
    //taking resources over
    size = org.size;
    data_ptr = org.data_ptr;

    //cleaning the orginal
    org.data_ptr = nullptr;
    org.size = 0;

}
//======================================================================================================================
Array & Array::operator=(const Array & org)
{
    if(&org != this ){
        delete[] data_ptr;

        size = org.size;
        auto elem_n = size*size;
        data_ptr = new T[elem_n];

        std::copy(org.data_ptr, org.data_ptr + (elem_n), data_ptr);
    }
    return *this;
}

Array &Array::operator=(Array && org)
{
    if(&org != this ){
        //preparing myself
        delete[] data_ptr;
        //taking resources over
        size = org.size;
        data_ptr = org.data_ptr;

        //cleaning the orginal
        org.data_ptr = nullptr;
        org.size = 0;
    }
    return *this;
}
//======================================================================================================================
T Array::get(std::size_t row, std::size_t col) const { return data_ptr[row*size + col]; }

void Array::set(T value, std::size_t row, std::size_t col){ (*this)[row][col] = value;}

const size_t Array::getSize(){ return size; }

T * Array::operator[](std::size_t row){ return (data_ptr + size * row);}


