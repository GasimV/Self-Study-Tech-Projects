#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

// Helper functions to calculate parent, left, and right indices
int Parent(int i) {
    return i / 2;
}

int Left(int i) {
    return 2 * i;
}

int Right(int i) {
    return 2 * i + 1;
}

void MAX_HEAPIFY(vector<int>& A, int i, int heap_size) {
    int l = Left(i);
    int r = Right(i);
    int largest = i;

    // Check if left child exists and is greater than the current largest
    if (l <= heap_size && A[l - 1] > A[i - 1]) { // Adjusting for 0-based indexing
        largest = l;
    }

    // Check if right child exists and is greater than the current largest
    if (r <= heap_size && A[r - 1] > A[largest - 1]) { // Adjusting for 0-based indexing
        largest = r;
    }

    // If the largest is not the current node
    if (largest != i) {
        // Swap elements
        swap(A[i - 1], A[largest - 1]);
        // Recursively heapify the affected subtree
        MAX_HEAPIFY(A, largest, heap_size);
    }
}

void BUILD_MAX_HEAP(vector<int>& A) {
    int heap_size = A.size();
    // Start from the last internal node and call MAX_HEAPIFY
    for (int i = heap_size / 2; i >= 1; --i) {
        MAX_HEAPIFY(A, i, heap_size);
    }
}

void Heapsort(vector<int>& A) {
    int heap_size = A.size();
    BUILD_MAX_HEAP(A);

    for (int i = heap_size; i >= 2; --i) {
        swap(A[0], A[i - 1]); // Move the max element to the end
        heap_size--;          // Reduce the heap size
        MAX_HEAPIFY(A, 1, heap_size);
    }
}

void print(const vector<int>& A) {
    for (int num : A) {
        cout << num << " ";
    }
    cout << endl;
}

int main() {
    vector<int> A1 = {16, 4, 10, 14, 7, 9, 3, 2, 8, 1};
    
    MAX_HEAPIFY(A1, 2, A1.size());
    cout << "The array after MAX_HEAPIFY: ";
    print(A1);
    
    vector<int> A2 = {4, 1, 3, 2, 16, 9, 10, 14, 8, 7};
    
    BUILD_MAX_HEAP(A2);
    cout << "The array after BUILD_MAX_HEAP: ";
    print(A2);

    Heapsort(A2);
    cout << "The array after Heapsort: ";
    print(A2);

    return 0;
}