#include "array.h"

using namespace pea;
using namespace std;
Array::Array(std::size_t n):
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
Array & Array::operator=(const Array &org)
{
    if(&org != this ){
        delete[] data_ptr;

        size = org.size;
        data_ptr = new T[size*size];

        for(size_t i=0; i < size*size; ++i)
            data_ptr[i] = org.data_ptr[i];
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
const T Array::get(std::size_t row, std::size_t col) { return data_ptr[row*size + col]; }

void Array::set(T value, std::size_t row, std::size_t col){ (*this)[row][col] = value;}

const size_t Array::getSize(){ return size; }

T * Array::operator[](std::size_t row){ return (data_ptr + size * row);}


