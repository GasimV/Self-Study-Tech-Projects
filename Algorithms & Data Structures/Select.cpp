#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>

using namespace std;

// Function to partition the array around the pivot
int PartitionAround(vector<int>& A, int p, int r, int pivot) {
    int pivotIndex = -1;
    for (int j = p; j <= r; ++j) {
        if (A[j] == pivot) {
            pivotIndex = j;
            break;
        }
    }
    swap(A[pivotIndex], A[r]);  // Move pivot to the end
    int x = A[r];  // Pivot element
    int i = p - 1;

    for (int j = p; j < r; ++j) {
        if (A[j] <= x) {
            i++;
            swap(A[i], A[j]);
        }
    }
    swap(A[i + 1], A[r]);  // Place pivot in its correct position
    return i + 1;  // Return the pivot index
}

// Function to select the i-th smallest element
int Select(vector<int>& A, int p, int r, int i) {
    while ((r - p + 1) % 5 != 0) {
        for (int j = p + 1; j <= r; ++j) {
            if (A[p] > A[j]) {
                swap(A[p], A[j]);
            }
        }
        if (i == 1) {
            return A[p];
        }
        p = p + 1;
        i = i - 1;
    }
    
    int g = (r - p + 1) / 5;
    for (int j = p; j <= p + g - 1; ++j) {
        sort(A.begin() + j, A.begin() + j + 5);
    }
    
    int x = Select(A, p + 2 * g, p + 3 * g - 1, ceil(g / 2.0));
    int q = PartitionAround(A, p, r, x);
    int k = q - p + 1;
    
    if (i == k) {
        return A[q];
    } else if (i < k) {
        return Select(A, p, q - 1, i);
    } else {
        return Select(A, q + 1, r, i - k);
    }
}

int main() {
    vector<int> A{6, 19, 4, 12, 14, 9, 15, 7, 8, 11, 3, 13, 2, 5, 10};
    
    int i = 5;
    int m = Select(A, 0, 14, i);
    cout << i << "th smallest element is: " << m;
    
    return 0;
}