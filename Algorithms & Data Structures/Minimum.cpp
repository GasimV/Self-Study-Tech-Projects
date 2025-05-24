#include <iostream>
#include <vector>

using namespace std;

int Minimum(vector<int>& A) {
    int n = A.size();
    
    int min = A[0];
    for (int i = 1; i < n; i++) {
        if (min > A[i]) {
            min = A[i];
        }
    }
    return min;
}

int main() {
    vector<int> A{78, 17, 39, 26, 72, 94, 21, 12, 23, 68};
    
    int m = Minimum(A);
    cout << m;
    
    return 0;
}