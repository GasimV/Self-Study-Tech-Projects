#include <iostream>

using namespace std;

// Node structure for doubly linked list (used in chaining)
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

// Doubly Linked List Class (Used for Chaining)
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

    // List-Delete(L, x) - Deletes node with key k
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

// Hash Table Class (Using Chaining)
class ChainedHashTable {
private:
    // Hash table size (Using a larger prime number for TABLE_SIZE can reduce collisions.)
    // Suggestion: Consider using dynamic resizing if the load factor becomes too high.
    static const int TABLE_SIZE = 7;
    DoublyLinkedList table[TABLE_SIZE]; // Array of linked lists for chaining

    // Hash function: h(k) = k mod TABLE_SIZE
    int hashFunction(int key) {
        return key % TABLE_SIZE;
    }

public:
    // Insert key into hash table
    void Insert(int key) {
        int index = hashFunction(key);
        table[index].ListPrepend(key);
    }

    // Search for a key
    bool Search(int key) {
        int index = hashFunction(key);
        return table[index].ListSearch(key) != nullptr;
    }

    // Delete key from hash table
    void Delete(int key) {
        int index = hashFunction(key);
        table[index].ListDelete(key);
    }

    // Print the entire hash table
    void PrintHashTable() {
        cout << "Hash Table State:\n";
        for (int i = 0; i < TABLE_SIZE; i++) {
            cout << "Index " << i << ": ";
            table[i].PrintList();
        }
        cout << endl;
    }
};

// Main function
int main() {
    ChainedHashTable hashTable;

    // Insert elements
    hashTable.Insert(1);
    hashTable.Insert(4);
    hashTable.Insert(5);
    hashTable.Insert(2);
    hashTable.Insert(6);
    hashTable.Insert(7);
    hashTable.Insert(3);
    hashTable.Insert(8);

    // Print initial table
    cout << "Initial Hash Table:\n";
    hashTable.PrintHashTable();

    // Search for key 5
    int searchKey = 5;
    if (hashTable.Search(searchKey)) {
        cout << "Key " << searchKey << " found in the hash table.\n";
    } else {
        cout << "Key " << searchKey << " not found in the hash table.\n";
    }

    // Delete key 5
    cout << "\nDeleting key 5...\n";
    hashTable.Delete(5);
    hashTable.PrintHashTable();

    return 0;
}