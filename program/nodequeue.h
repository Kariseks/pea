#ifndef NODEQUEUE_H
#define NODEQUEUE_H

#include "node.h"
#include <utility>

class NodeQueue {
private:
    struct QueueElement {
        Node data;
        QueueElement* next;

        // Konstruktor kopiujący
        QueueElement(const Node& val) : data(val), next(nullptr) {}

        // Konstruktor przenoszący dla wydajności
        QueueElement(Node&& val) : data(std::move(val)), next(nullptr) {}
    };

    QueueElement* head;
    QueueElement* tail;

public:
    NodeQueue() : head(nullptr), tail(nullptr) {}

    // Destruktor - zwalnia całą pamięć (wymóg dynamicznej alokacji)
    ~NodeQueue() {
        while (!empty()) {
            pop();
        }
    }

    // Blokujemy kopiowanie
    NodeQueue(const NodeQueue&) = delete;
    NodeQueue& operator=(const NodeQueue&) = delete;

    // Dodawanie na koniec kolejki (wersja kopiująca)
    void push(const Node& value) {
        QueueElement* newElem = new QueueElement(value);
        if (empty()) {
            head = tail = newElem;
        } else {
            tail->next = newElem;
            tail = newElem;
        }
    }

    // Dodawanie na koniec kolejki (wersja przenosząca)
    void push(Node&& value) {
        QueueElement* newElem = new QueueElement(std::move(value));
        if (empty()) {
            head = tail = newElem;
        } else {
            tail->next = newElem;
            tail = newElem;
        }
    }

    // Usuwanie z przodu kolejki
    void pop() {
        if (!empty()) {
            QueueElement* temp = head;
            head = head->next;
            if (head == nullptr) {
                tail = nullptr; // Jeśli kolejka stała się pusta
            }
            delete temp;
        }
    }

    // Zwraca referencję do pierwszego elementu
    Node& front() {
        return head->data;
    }

    // Sprawdza, czy kolejka jest pusta
    bool empty() const {
        return head == nullptr;
    }
};

#endif // NODEQUEUE_H