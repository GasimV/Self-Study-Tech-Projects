#include <iostream>

void BubbleSort(int A[], int n) {
    for (int i = 0; i < n - 1; i++) { // i runs from 0 to n-2
        for (int j = n - 1; j > i; j--) { // j runs from n-1 down to i+1
            if (A[j] < A[j - 1]) { // Compare A[j] with A[j-1]
                std::swap(A[j], A[j - 1]); // Swap if needed
            }
        }
    }
}

void PrintArray(int A[], int n) {
    for (int i = 0; i < n; i++) {
        std::cout << A[i] << " ";
    }
    std::cout << std::endl;
}

int main() {
    int A[5] = {5, 7, 3, 1, 0}; // Example array
    int n = sizeof(A) / sizeof(A[0]); // Get the size of the array (in bytes): 20 / 4 = 5

    std::cout << "Original array: ";
    PrintArray(A, n);
    
    BubbleSort(A, n);

    std::cout << "Sorted array: ";
    PrintArray(A, n);

    return 0;
}