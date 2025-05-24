#include <iostream>
#include <vector>

using namespace std;

vector<int> CountingSort(const vector<int>& A, int k) {
    int n = A.size();
    vector<int> B(n); // Output array
    vector<int> C(k + 1, 0); // Count (auxiliary) array initialized to 0

    // Step 1: Count the occurrences of each value in A
    for (int j = 0; j < n; ++j) {
        C[A[j]]++;
    }
    
    // Step 2: Compute the prefix sums in C
    for (int i = 1; i <= k; ++i) {
        C[i] += C[i - 1];
    }
    
    // Step 3: Build the sorted array B
    for (int j = n - 1; j >= 0; --j) {
        B[C[A[j]] - 1] = A[j];
        C[A[j]]--; // to handle duplicate values
    }

    return B;
}

void Print(const vector<int>& Array) {
    for (int i : Array) {
        cout << i << ' ';
    }
    cout << endl;
}

int main() {
    vector<int> Array{2, 5, 3, 0, 2, 3, 0, 3};
    
    vector<int> sorted = CountingSort(Array, 5);
    Print(sorted);
    
    return 0;
}