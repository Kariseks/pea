#include "wektor.h"
#include <algorithm>

using namespace std;

Wektor::Wektor(std::initializer_list<T> list):
    capacity{list.size()},
    size(list.size())
{
    data_ptr = new T[capacity];
    std::copy(list.begin(), list.end(), data_ptr);

}

Wektor::Wektor(std::size_t init_size):
    capacity{init_size},
    size{init_size}
{
    data_ptr = new T[size];
}


Wektor::Wektor(const Wektor & org) noexcept
{
    size = org.size;
    capacity = org.capacity;
    data_ptr = new T[capacity];
    copy(org);
}

Wektor::Wektor(Wektor && org) noexcept
{
    size = org.size;
    capacity = org.capacity;
    data_ptr = org.data_ptr;

    org.size = 0;
    org.capacity = 0;
    org.data_ptr = nullptr;
}

Wektor & Wektor::operator=(const Wektor & org)
{
    if(this != &org)
    {
        auto old_data_ptr = data_ptr;

        data_ptr = new T[org.capacity];
        size = org.size;
        capacity = org.capacity;

        delete[] old_data_ptr;
        copy(org);
    }
    return *this;
}
Wektor &Wektor::operator=(Wektor && org)
{
    if(this != &org)
    {
        delete[] data_ptr;

        size = org.size;
        capacity = org.capacity;
        data_ptr = org.data_ptr;

        org.size = 0;
        org.capacity = 0;
        org.data_ptr = nullptr;
    }
    return *this;
}

Wektor::~Wektor()
{
    delete[] data_ptr;
}

T &Wektor::operator[](std::size_t idx)
{
    return *(data_ptr+idx);
}

bool Wektor::push_back(const T & elem)
{
    //1 check size
    if(size == capacity)
    {
        auto old_data_ptr = data_ptr;
        capacity = growPolicy();
        data_ptr = new T[capacity];

        for(size_t i=0; i<size; ++i)
            data_ptr[i] = std::move(old_data_ptr[i]);

        delete[] old_data_ptr;
    }

    data_ptr[size] = elem;
    ++size;
    return true;
}

void Wektor::copy(const Wektor & org)
{
    for(std::size_t i=0; i<org.size; ++i)
        data_ptr[i] = org.data_ptr[i];
}

void Wektor::move(Wektor && org)
{
    for(std::size_t i=0; i<org.size; ++i)
        data_ptr[i] = std::move(data_ptr[i]);
}

std::size_t Wektor::growPolicy()
{
    if(capacity < 10)
        return 10;
    return capacity * growFactor;
}

