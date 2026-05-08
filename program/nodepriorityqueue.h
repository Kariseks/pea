#ifndef NODEPRIORITYQUEUE_H
#define NODEPRIORITYQUEUE_H

#include "node.h"
//#include <utility>

class NodePriorityQueue {
private:
    struct QueueElement {
        Node data;
        QueueElement* next;

        QueueElement(const Node& val) : data(val), next(nullptr) {}
        QueueElement(Node&& val) : data(std::move(val)), next(nullptr) {}
    };

    QueueElement* head;

public:
    NodePriorityQueue() : head(nullptr) {}

    ~NodePriorityQueue() {
        while (!empty()) {
            pop();
        }
    }

    NodePriorityQueue(const NodePriorityQueue&) = delete;
    NodePriorityQueue& operator=(const NodePriorityQueue&) = delete;

    // Wstawianie z zachowaniem porządku rosnącego według 'bound' (wersja przenosząca)
    void push(Node&& value) {
        QueueElement* newElem = new QueueElement(std::move(value));

        // Jeśli kolejka jest pusta LUB nowy element ma mniejszy 'bound' niż głowa
        if (head == nullptr || newElem->data.bound < head->data.bound) {
            newElem->next = head;
            head = newElem;
        } else {
            // Szukamy odpowiedniego miejsca w posortowanej liście
            QueueElement* current = head;
            while (current->next != nullptr && current->next->data.bound <= newElem->data.bound) {
                current = current->next;
            }
            newElem->next = current->next;
            current->next = newElem;
        }
    }

    // Wstawianie z zachowaniem porządku (wersja kopiująca)
    void push(const Node& value) {
        QueueElement* newElem = new QueueElement(value);

        if (head == nullptr || newElem->data.bound < head->data.bound) {
            newElem->next = head;
            head = newElem;
        } else {
            QueueElement* current = head;
            while (current->next != nullptr && current->next->data.bound <= newElem->data.bound) {
                current = current->next;
            }
            newElem->next = current->next;
            current->next = newElem;
        }
    }

    // Usuwanie elementu o najniższym koszcie (zawsze na początku listy)
    void pop() {
        if (head != nullptr) {
            QueueElement* temp = head;
            head = head->next;
            delete temp;
        }
    }

    // Pobranie elementu o najniższym koszcie
    Node& top() {
        return head->data;
    }

    bool empty() const {
        return head == nullptr;
    }
};

#endif // NODEPRIORITYQUEUE_H