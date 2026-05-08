#ifndef NODESTACK_H
#define NODESTACK_H

#include "node.h"
#include <utility>

class NodeStack {
private:
    // Prywatna struktura elementu listy przechowująca pojedynczy Node
    struct StackElement {
        Node data;
        StackElement* next;

        // Konstruktor kopiujący dla danych
        StackElement(const Node& val, StackElement* nxt)
            : data(val), next(nxt) {}

        // Konstruktor przenoszący dla danych (dla wysokiej wydajności)
        StackElement(Node&& val, StackElement* nxt)
            : data(std::move(val)), next(nxt) {}
    };

    StackElement* head;

public:
    // Konstruktor
    NodeStack() : head(nullptr) {}

    // Destruktor - zwalnia całą pamięć (wymóg dynamicznej alokacji)
    ~NodeStack() {
        while (!empty()) {
            pop();
        }
    }

    // Blokujemy kopiowanie stosu, aby uniknąć wycieków pamięci i błędów
    NodeStack(const NodeStack&) = delete;
    NodeStack& operator=(const NodeStack&) = delete;

    // Metoda Push (wersja kopiująca)
    void push(const Node& value) {
        head = new StackElement(value, head);
    }

    // Metoda Push (wersja przenosząca r-value)
    void push(Node&& value) {
        head = new StackElement(std::move(value), head);
    }

    // Metoda Pop - usuwa element z wierzchołka
    void pop() {
        if (head != nullptr) {
            StackElement* temp = head;
            head = head->next;
            delete temp;
        }
    }

    // Zwraca referencję do elementu na wierzchołku
    Node& top() {
        return head->data;
    }

    // Sprawdza, czy stos jest pusty
    bool empty() const {
        return head == nullptr;
    }
};

#endif // NODESTACK_H