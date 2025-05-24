#include <iostream>
#include <vector>

using namespace std;

int Partition(vector<int>& A, int p, int r) {
    int x = A[r]; // the pivot
    int i = p - 1; // highest index into the low side
    
    for (int j = p; j < r; ++j) { // process each element other than the pivot
        if (A[j] <= x) { // does this element belong on the low side?
            i++; // index of a new slot in the low side
            swap(A[i], A[j]); // put this element there
        }
    }
    swap(A[i + 1], A[r]); // pivot goes just to the right of the low side
    
    return i + 1; // new index of the pivot
}

void Quicksort(vector<int>& A, int p, int r) {
    if (p < r) {
        // Partition the subarray around the pivot, which ends up in A[q].
        int q = Partition(A, p, r);
        Quicksort(A, p, q - 1); // recursively sort the low side
        Quicksort(A, q + 1, r); // recursively sort the high side
    }
}

void Print(const vector<int>& Array) {
    for (int i : Array) {
        cout << i << ' ';
    }
    cout << endl;
}

int main() {
    vector<int> A{2, 8, 7, 1, 3, 5, 6, 4};
    
    int start = 0;
    int end = A.size() - 1;
    
    cout << "Array after the Partition Operation: " << endl;
    Partition(A, start, end);
    Print(A);
    
    cout << "Array after the Quicksort Operation: " << endl;
    Quicksort(A, start, end);
    Print(A);
}