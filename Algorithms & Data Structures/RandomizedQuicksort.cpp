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

int RandomIndex(int p, int r) {
    return p + rand() % (r - p + 1); // random index between p and r
}

int RandomizedPartition(vector<int>& A, int p, int r) {
    int i = RandomIndex(p, r); // get a random index
    swap(A[r], A[i]); // move the random element to the end
    return Partition(A, p, r); // use the standard partition function
}

void RandomizedQuicksort(vector<int>& A, int p, int r) {
    if (p < r) {
        int q = RandomizedPartition(A, p, r);
        RandomizedQuicksort(A, p, q - 1);
        RandomizedQuicksort(A, q + 1, r);
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

    // Seed the random number generator
    srand(static_cast<unsigned>(time(0)));

    RandomizedQuicksort(A, start, end);
    cout << "\nArray after Randomized Quicksort: ";
    Print(A);

    return 0;
}