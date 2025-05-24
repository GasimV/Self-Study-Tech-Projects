#include <iostream>
#include <vector>

using namespace std;

// Modified CountingSort to work with specific digits
vector<int> CountingSortForRadix(const vector<int>& A, int exp) {
    int n = A.size();
    vector<int> B(n); // Output array
    vector<int> C(10, 0); // Count array for digits 0-9

    // Step 1: Count occurrences of each digit at the current place (exp)
    for (int i = 0; i < n; ++i) {
        int digit = (A[i] / exp) % 10;
        C[digit]++;
    }

    // Step 2: Compute the prefix sums in C
    for (int i = 1; i < 10; ++i) {
        C[i] += C[i - 1];
    }

    // Step 3: Build the sorted array B
    for (int i = n - 1; i >= 0; --i) {
        int digit = (A[i] / exp) % 10;
        B[C[digit] - 1] = A[i];
        C[digit]--; // Decrement count for the digit
    }

    return B;
}

// Function to find the maximum value in the array
int getMax(const vector<int>& arr) {
    int mx = arr[0];
    for (int i = 1; i < static_cast<int>(arr.size()); i++) {
        if (arr[i] > mx)
            mx = arr[i];
    }
    return mx;
}

// Radix Sort
void RadixSort(vector<int>& A) {
    // Find the maximum number to know the number of digits
    int maxVal = getMax(A);
    
    // Sort by each digit (starting with least significant digit)
    for (int exp = 1; maxVal / exp > 0; exp *= 10) {
        A = CountingSortForRadix(A, exp);
    }
}

void Print(const vector<int>& Array) {
    for (int i : Array) {
        cout << i << ' ';
    }
    cout << endl;
}

int main() {
    vector<int> Array{329, 457, 657, 839, 436, 720, 355};
    
    cout << "Original array: ";
    Print(Array);
    
    RadixSort(Array);
    
    cout << "Sorted array: ";
    Print(Array);
    
    return 0;
}