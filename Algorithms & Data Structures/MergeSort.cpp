#include <iostream>
#include <vector>

using namespace std;

// p – start; q – midpoint; r – end.
void Merge(vector<int>& A, int p, int q, int r) {
    // Length of Left Subarray A[p:q]
    int n_l = q - p + 1;
    // Length of Right Subarray A[q+1:r]
    int n_r = r - q;
    
    // L (Left) and R (Right) Temporary Arrays
    vector<int> L(n_l);
    vector<int> R(n_r);

    // Copy A[p:q] into L[0:n_l-1]
    for (int i = 0; i < n_l; ++i) {
        L[i] = A[p + i];
    }
    
    // Copy A[q+1:r] into R[0:n_r-1]
    for (int j = 0; j < n_r; ++j) {
        R[j] = A[q + 1 + j];
    }
    
    // Merge L and R back into A[p:r]
    int i = 0, j = 0, k = p;

    while (i < n_l && j < n_r) {
        if (L[i] <= R[j]) {
            A[k] = L[i];
            i++;
        } else {
            A[k] = R[j];
            j++;
        }
        k++;
    }
    
    // Copy any remaining elements from L
    while (i < n_l) {
        A[k] = L[i];
        i++;
        k++;
    }
    
    // Copy any remaining elements from R
    while (j < n_r) {
        A[k] = R[j];
        j++;
        k++;
    }
}

void MergeSort(vector<int>& A, int p, int r) {
    // Base case: 0 or 1 element
    if (p >= r) {
        return;
    }
    // midpoint of A[p:r]
    int q = (p + r) / 2;
    // recursively sort A[p:q]
    MergeSort(A, p, q);
    // recursively sort A[q+1:r]
    MergeSort(A, q+1, r);
    
    // Merge A[p:q] and A[q+1:r] into A[p:r].
    Merge(A, p, q, r);
}

int main() {
    vector<int> A{5, 2, 4, 6, 1, 3};
    
	// p = 0 (start); r = A.size() – 1 (end).
	// Sort the entire array (from index 0 to size-1).
    int start = 0;
    int end = A.size() - 1;

    MergeSort(A, start, end);
    
    // Output sorted array
    for (int i : A) {
        cout << i << ' ';
    }
    cout << endl;

    return 0;
}
