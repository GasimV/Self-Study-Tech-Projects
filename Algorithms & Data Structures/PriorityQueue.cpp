#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>

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

int MAX_HEAP_MAXIMUM(const vector<int>& A) {
    if (A.empty()) {
        throw underflow_error("Heap underflow");
    }
    return A[0]; // The maximum element is at the root of the max-heap
}

int MAX_HEAP_EXTRACT_MAX(vector<int>& A) {
    if (A.empty()) {
        throw underflow_error("Heap underflow");
    }
    int max = A[0];
    A[0] = A[A.size() - 1]; // Replace root with the last element
    A.pop_back(); // Remove the last element
    MAX_HEAPIFY(A, 1, A.size());
    return max;
}

void MAX_HEAP_INCREASE_KEY(vector<int>& A, int i, int key) {
    if (key < A[i - 1]) {
        throw invalid_argument("New key is smaller than current key");
    }
    A[i - 1] = key;
    while (i > 1 && A[Parent(i) - 1] < A[i - 1]) {
        swap(A[i - 1], A[Parent(i) - 1]);
        i = Parent(i);
    }
}

void MAX_HEAP_INSERT(vector<int>& A, int key) {
    A.push_back(INT_MIN); // Append a dummy value at the end
    MAX_HEAP_INCREASE_KEY(A, A.size(), key);
}

void print(const vector<int>& A) {
    for (int num : A) {
        cout << num << " ";
    }
    cout << endl;
}

int main() {
    vector<int> A = {16, 4, 10, 14, 7, 9, 3, 2, 8, 1};
    BUILD_MAX_HEAP(A);

    cout << "Initial max-heap: ";
    print(A);

    // Test MAX_HEAP_MAXIMUM
    cout << "Maximum element: " << MAX_HEAP_MAXIMUM(A) << endl;

    // Test MAX_HEAP_EXTRACT_MAX
    int max = MAX_HEAP_EXTRACT_MAX(A);
    cout << "Extracted maximum: " << max << endl;
    cout << "Heap after extraction: ";
    print(A);

    // Test MAX_HEAP_INCREASE_KEY
    MAX_HEAP_INCREASE_KEY(A, 5, 15);
    cout << "Heap after increasing key at index 5 to 15: ";
    print(A);

    // Test MAX_HEAP_INSERT
    MAX_HEAP_INSERT(A, 20);
    cout << "Heap after inserting 20: ";
    print(A);

    return 0;
}