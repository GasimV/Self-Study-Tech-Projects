#include <iostream>

using namespace std;

// Node structure for doubly linked list
struct Node {
    int key;
    Node* prev;
    Node* next;

    // Constructor
    Node(int val) {
        key = val;
        prev = nullptr;
        next = nullptr;
    }
};

// Doubly Linked List Class
class DoublyLinkedList {
private:
    Node* head; // Points to the first node

public:
    // Constructor
    DoublyLinkedList() {
        head = nullptr;
    }

    // List-Search(L, k) - Searches for the first occurrence of k
    Node* ListSearch(int k) {
        Node* x = head;
        while (x != nullptr && x->key != k) {
            x = x->next;
        }
        return x; // Returns nullptr if not found, else pointer to node
    }

    // List-Prepend(L, x) - Inserts x at the front
    void ListPrepend(int k) {
        Node* x = new Node(k);
        x->next = head;
        x->prev = nullptr;
        if (head != nullptr) {
            head->prev = x;
        }
        head = x; // Update head to the new node
    }

    // List-Insert(x, y) - Inserts x after y
    void ListInsert(int k, int keyAfter) {
        Node* y = ListSearch(keyAfter);
        if (y == nullptr) {
            cout << "Error: Element " << keyAfter << " not found!" << endl;
            return;
        }
        Node* x = new Node(k);
        x->next = y->next;
        x->prev = y;
        if (y->next != nullptr) {
            y->next->prev = x;
        }
        y->next = x;
    }

    // List-Delete(L, x) - Deletes node x
    void ListDelete(int k) {
        Node* x = ListSearch(k);
        if (x == nullptr) {
            cout << "Error: Element " << k << " not found!" << endl;
            return;
        }
        if (x->prev != nullptr) {
            x->prev->next = x->next;
        } else {
            head = x->next; // If deleting head, move it forward
        }
        if (x->next != nullptr) {
            x->next->prev = x->prev;
        }
        delete x;
    }

    // Print List Forward
    void PrintList() {
        Node* temp = head;
        while (temp != nullptr) {
            cout << temp->key << " ";
            temp = temp->next;
        }
        cout << endl;
    }

    // Destructor to free memory
    ~DoublyLinkedList() {
        Node* temp = head;
        while (temp != nullptr) {
            Node* nextNode = temp->next;
            delete temp;
            temp = nextNode;
        }
    }
};

int main() {
    DoublyLinkedList dll;

    // Step (a): Initial linked list {1, 4, 16, 9}
    dll.ListPrepend(1);
    dll.ListPrepend(4);
    dll.ListPrepend(16);
    dll.ListPrepend(9);

    cout << "(a) Initial List: ";
    dll.PrintList();

    // Step (b): Perform LIST-PREPEND(L, x) with x = 25
    dll.ListPrepend(25);
    cout << "(b) After Prepending 25: ";
    dll.PrintList();

    // Step (c): Perform LIST-INSERT(x, y) with x = 36, y = 9
    dll.ListInsert(36, 9);
    cout << "(c) After Inserting 36 after 9: ";
    dll.PrintList();

    // Step (d): Perform LIST-DELETE(L, x) where x.key = 4
    dll.ListDelete(4);
    cout << "(d) After Deleting 4: ";
    dll.PrintList();

    return 0;
}