#include <iostream>

#define NIL -1 // Represents an empty slot

using namespace std;

class OpenAddressingHashTable {
private:
    int* table;      // Dynamic array for storing keys
    int  TABLE_SIZE; // Hash table size

    // Hash function with linear probing
    // h(k,i) = (k + i) % TABLE_SIZE
    int hashFunction(int key, int i) const {
        return (key + i) % TABLE_SIZE;
    }

public:
    // Constructor - Initializes table with given size
    OpenAddressingHashTable(int size) {
        TABLE_SIZE = size;
        table = new int[TABLE_SIZE];
        for (int i = 0; i < TABLE_SIZE; i++) {
            table[i] = NIL;
        }
    }

    // Hash-Insert(T, k)
    int HashInsert(int key) {
        int i = 0;
        while (i < TABLE_SIZE) {
            int q = hashFunction(key, i);
            if (table[q] == NIL) {
                table[q] = key;
                return q;
            }
            i++;
        }
        cout << "Error: Hash table overflow!" << endl;
        return -1; // Indicating failure
    }

    // Hash-Search(T, k)
    int HashSearch(int key) const {
        int i = 0;
        while (i < TABLE_SIZE) {
            int q = hashFunction(key, i);
            if (table[q] == key) {
                return q; // Key found
            }
            if (table[q] == NIL) {
                return -1; // Key not present (hit empty slot)
            }
            i++;
        }
        return -1; // Key not found after full scan
    }

    // Hash-Delete(T, key)
    void HashDelete(int key) {
        // First find the slot where 'key' resides
        int q = HashSearch(key);
        if (q == -1) {
            cout << "Error: Key " << key << " not found in hash table!" << endl;
            return;
        }

        // According to CLRS pseudocode:
        //   LINEAR-PROBING-HASH-DELETE(T,q):
        //   1  while TRUE
        //   2    T[q] = NIL
        //   3    q' = q
        //   4    repeat
        //   5        q' = (q' + 1) mod m
        //   6        k' = T[q']
        //   7        if k' == NIL
        //   8            return
        //   9    until g(k',q) < g(k',q')
        //  10    T[q] = k'
        //  11    q = q'
        
        while (true) {
            // Empty the slot at index q
            table[q] = NIL;

            // Start scanning from q
            int q_prime = q;

            // Keep moving forward until you find a key that should move back
            while (true) {
                // Move to the next slot in linear probing
                q_prime = (q_prime + 1) % TABLE_SIZE;

                int k_prime = table[q_prime];
                // If we hit an empty slot, we're done
                if (k_prime == NIL) {
                    return;
                }

                // Otherwise, compute how far k_prime has probed:
                // h(k_prime) is simply (k_prime % TABLE_SIZE) for i=0 in this code
                int basePos  = k_prime % TABLE_SIZE;

                // g(k_prime, q)     = (q - basePos) mod TABLE_SIZE
                // g(k_prime, q_prime) = (q_prime - basePos) mod TABLE_SIZE
                int g_q      = (q - basePos + TABLE_SIZE) % TABLE_SIZE;
                int g_qPrime = (q_prime - basePos + TABLE_SIZE) % TABLE_SIZE;

                // If k_prime wants to be "closer to" q (fewer probes) than q_prime
                // i.e. g(k_prime, q) < g(k_prime, q_prime)
                // move it back into slot q.
                if (g_q < g_qPrime) {
                    table[q] = k_prime;   // Move k_prime into the freed slot
                    table[q_prime] = NIL; // That frees up slot q_prime
                    q = q_prime;          // Now slot q_prime is the newly freed slot
                    break;                // Break out of inner loop; continue outer
                }
                // Otherwise, keep scanning forward until we find a key that does belong
                // or we find an empty slot.
            }
            // We re-empty slot q (the newly freed slot) and repeat the process
        }
    }

    // Display Hash Table
    void PrintTable() const {
        cout << "Hash Table: " << endl;
        for (int i = 0; i < TABLE_SIZE; i++) {
            if (table[i] == NIL) {
                cout << "[" << i << "]: NIL" << endl;
            } else {
                cout << "[" << i << "]: " << table[i] << endl;
            }
        }
        cout << endl;
    }

    // Destructor - Free allocated memory
    ~OpenAddressingHashTable() {
        delete[] table;
    }
};

int main() {
    int tableSize;
    cout << "Enter table size: ";
    cin >> tableSize;

    OpenAddressingHashTable hashTable(tableSize);

    // Insert some elements
    hashTable.HashInsert(74);
    hashTable.HashInsert(43);
    hashTable.HashInsert(93);
    hashTable.HashInsert(18);
    hashTable.HashInsert(82);
    hashTable.HashInsert(38);
    hashTable.HashInsert(92);

    cout << "After Insertions:" << endl;
    hashTable.PrintTable();

    // Test search operation
    cout << "Testing Search Operation:" << endl;
    int searchKeys[] = {43, 74, 100}; // Searching for existing & non-existing keys
    for (int key : searchKeys) {
        int result = hashTable.HashSearch(key);
        if (result != -1)
            cout << "Key " << key << " found at index " << result << endl;
        else
            cout << "Key " << key << " not found in the table." << endl;
    }
    cout << endl;

    // Delete key 43
    hashTable.HashDelete(43);

    cout << "After Deleting 43:" << endl;
    hashTable.PrintTable();

    return 0;
}