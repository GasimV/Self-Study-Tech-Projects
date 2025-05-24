#include <iostream>

using namespace std;

#define UNIVERSE_SIZE 10 // Define the universe size (0 to 9)

// Structure for an element in the direct-address table
struct Element {
    int key;
    int satelliteData; // Additional data stored in the element

    // Constructor
    Element(int k, int data) {
        key = k;
        satelliteData = data;
    }
};

// Class for Direct-Address Table (Using Raw Array)
class DirectAddressTable {
private:
    Element* table[UNIVERSE_SIZE]; // Raw array to store pointers

public:
    // Constructor: Initialize table with nullptrs
    DirectAddressTable() {
        for (int i = 0; i < UNIVERSE_SIZE; i++) {
            table[i] = nullptr;
        }
    }

    // Direct-Address-Search(T, k) → Returns pointer to element or nullptr
    Element* Search(int k) {
        if (k < 0 || k >= UNIVERSE_SIZE) return nullptr; // Out of bounds
        return table[k]; // Return element or nullptr
    }

    // Direct-Address-Insert(T, x) → Inserts an element x
    void Insert(int key, int data) {
        if (key < 0 || key >= UNIVERSE_SIZE) {
            cout << "Error: Key " << key << " is out of bounds!" << endl;
            return;
        }
        if (table[key] != nullptr) {
            cout << "Warning: Key " << key << " already exists! Overwriting..." << endl;
            delete table[key]; // Remove old element
        }
        table[key] = new Element(key, data);
    }

    // Direct-Address-Delete(T, x) → Deletes element x
    void Delete(int key) {
        if (key < 0 || key >= UNIVERSE_SIZE) {
            cout << "Error: Key " << key << " is out of bounds!" << endl;
            return;
        }
        if (table[key] == nullptr) {
            cout << "Warning: Key " << key << " does not exist!" << endl;
            return;
        }
        delete table[key]; // Free memory
        table[key] = nullptr; // Mark as empty
    }

    // Print the current table state
    void PrintTable() {
        cout << "Direct-Address Table:" << endl;
        for (int i = 0; i < UNIVERSE_SIZE; i++) {
            if (table[i] != nullptr) {
                cout << "Index " << i << ": Key = " << table[i]->key 
                     << ", Data = " << table[i]->satelliteData << endl;
            } else {
                cout << "Index " << i << ": NIL" << endl;
            }
        }
        cout << endl;
    }

    // Destructor to free memory
    ~DirectAddressTable() {
        for (int i = 0; i < UNIVERSE_SIZE; i++) {
            if (table[i] != nullptr) {
                delete table[i];
            }
        }
    }
};

// Main function to test direct-address table
int main() {
    DirectAddressTable T;

    // Insert elements as per the book's example
    T.Insert(2, 3);
    T.Insert(3, 3);
    T.Insert(5, 5);
    T.Insert(8, 8);

    // Print initial table
    cout << "Initial Table:" << endl;
    T.PrintTable();

    // Search operation
    int searchKey = 5;
    Element* found = T.Search(searchKey);
    if (found) {
        cout << "Search Key " << searchKey << ": Found! Data = " << found->satelliteData << endl;
    } else {
        cout << "Search Key " << searchKey << ": Not Found!" << endl;
    }

    // Delete key 3
    cout << "\nDeleting key 3..." << endl;
    T.Delete(3);
    T.PrintTable();

    // Try deleting a non-existing key
    cout << "Deleting key 7 (not in table)..." << endl;
    T.Delete(7);
    T.PrintTable();

    return 0;
}