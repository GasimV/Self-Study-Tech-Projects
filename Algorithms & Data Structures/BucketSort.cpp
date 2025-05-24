#include <iostream>
#include <vector>

using namespace std;

// Insertion Sort
void InsertionSort(vector<float>& A) {
    int n = A.size();
    for (int i = 1; i < n; i++) {
        float key = A[i];
        int j = i - 1;
        while (j >= 0 && key < A[j]) {
            A[j + 1] = A[j];
            j--;
        }
        A[j + 1] = key;
    }
}

// Bucket Sort
void BucketSort(vector<float>& A) {
    int n = A.size();
    
    // Step 1: Create n empty buckets
    vector<vector<float>> B(n);
    
    // Step 2: Put array elements in different buckets
    for (int i = 0; i < n; i++) {
        int bucketIndex = n * A[i]; // Assuming A[i] is in range [0, 1)
        
        // If there's a chance of floating-point imprecision causing A[i] to equal 1.0, 
        // you might want to handle it explicitly to avoid an out-of-range bucket index:
        // int bucketIndex = min(n - 1, static_cast<int>(n * A[i]));

        B[bucketIndex].push_back(A[i]);
    }
    
    // Step 3: Sort each bucket using Insertion Sort
    for (int i = 0; i < n; i++) {
        InsertionSort(B[i]);
    }
    
    // Step 4: Concatenate all buckets into the original array
    int index = 0;
    for (int i = 0; i < n; i++) {
        for (size_t j = 0; j < B[i].size(); j++) {
            A[index++] = B[i][j];
        }
    }
}

int main() {
    vector<float> A{.78, .17, .39, .26, .72, .94, .21, .12, .23, .68};
    
    BucketSort(A);
    
    for (float num : A) {
        cout << num << ' ';
    }
    cout << endl;
    
    return 0;
}