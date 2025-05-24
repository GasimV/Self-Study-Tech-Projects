#include <vector>
#include <iostream>

using namespace std;

int main() {
    vector<int> A{ 5, 2, 4, 6, 1, 3 };
    int n = A.size();
    
    for (int i = 1; i < n; i++) {
        int key = A[i];
        int j = i - 1;
        
        while (j >= 0 && key < A[j]) {
            A[j + 1] = A[j];
            j--;
        }
        
        A[j + 1] = key;
    }
    
    for (int i : A) {
        cout << i << ' ';
    }
}
