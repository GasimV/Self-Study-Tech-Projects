#include <iostream>

using namespace std;

// Node structure for doubly linked list with a sentinel
struct Node {
    int key;
    Node* prev;
    Node* next;

    // Constructor
    Node(int val = 0) { // Default constructor for sentinel (key 0)
        key = val;
        prev = nullptr;
        next = nullptr;
    }
};

// Circular Doubly Linked List with Sentinel
class DoublyLinkedListWithSentinel {
private:
    Node* nil; // Sentinel node

public:
    // Constructor - Initializes the sentinel
    DoublyLinkedListWithSentinel() {
        nil = new Node(); // Create sentinel node
        nil->next = nil;  // Sentinel points to itself
        nil->prev = nil;
    }

    // List-Search'(L, k) - Searches for key k
    Node* ListSearch(int k) {
        nil->key = k;  // Store key in sentinel to guarantee it is in the list
        Node* x = nil->next; // Start at the head
        while (x->key != k) {
            x = x->next;
        }
        return (x == nil) ? nullptr : x; // Return nullptr if only found in sentinel
    }

    // List-Insert'(x, y) - Inserts x after y
    void ListInsert(int k, Node* y) {
        Node* x = new Node(k);
        x->next = y->next;
        x->prev = y;
        y->next->prev = x;
        y->next = x;
    }

    // Insert at Head (L.nil.next)
    void InsertAtHead(int k) {
        ListInsert(k, nil);
    }

    // Insert at Tail (L.nil.prev)
    void InsertAtTail(int k) {
        ListInsert(k, nil->prev);
    }

    // List-Delete'(x) - Deletes a given node x
    void ListDelete(Node* x) {
        if (x == nil) return; // Do not delete the sentinel!
        x->prev->next = x->next;
        x->next->prev = x->prev;
        delete x;
    }

    // Print the list
    void PrintList() {
        Node* temp = nil->next;
        while (temp != nil) { // Stop at sentinel
            cout << temp->key << " ";
            temp = temp->next;
        }
        cout << endl;
    }

    // Destructor to free memory
    ~DoublyLinkedListWithSentinel() {
        Node* temp = nil->next;
        while (temp != nil) {
            Node* nextNode = temp->next;
            delete temp;
            temp = nextNode;
        }
        delete nil;
    }
};

// Main function to test sentinel-based implementation
int main() {
    DoublyLinkedListWithSentinel dll;

    // Step (a) - Initially Empty List
    cout << "(a) Empty List: ";
    dll.PrintList();

    // Step (b) - Insert {9, 16, 4, 1} at tail
    dll.InsertAtTail(9);
    dll.InsertAtTail(16);
    dll.InsertAtTail(4);
    dll.InsertAtTail(1);
    cout << "(b) List after inserting {9, 16, 4, 1}: ";
    dll.PrintList();

    // Step (c) - Insert 25 at head
    dll.InsertAtHead(25);
    cout << "(c) After inserting 25 at head: ";
    dll.PrintList();

    // Step (d) - Delete node with key 1
    Node* toDelete = dll.ListSearch(1);
    if (toDelete) dll.ListDelete(toDelete);
    cout << "(d) After deleting 1: ";
    dll.PrintList();

    // Step (e) - Insert 36 after 9
    Node* insertAfter = dll.ListSearch(9);
    if (insertAfter) dll.ListInsert(36, insertAfter);
    cout << "(e) After inserting 36 after 9: ";
    dll.PrintList();

    return 0;
}