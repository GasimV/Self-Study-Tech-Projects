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

int RandomizedSelect(vector<int>& A, int p, int r, int i) {
    if (p == r)
        return A[p]; // 1 <= i <= r - p + 1 when p == r means that i = 1
        
    int q = RandomizedPartition(A, p, r);
    int k = q - p + 1;
    
    if (i == k)
        return A[q]; // the pivot value is the answer
    else if (i < k)
        return RandomizedSelect(A, p, q-1, i);
    else return RandomizedSelect(A, q+1, r, i-k);
}

int main() {
    vector<int> A{6, 19, 4, 12, 14, 9, 15, 7, 8, 11, 3, 13, 2, 5, 10};
    
    int i = 5;
    int m = RandomizedSelect(A, 0, 14, i);
    cout << i << "th smallest element is: " << m;
    
    return 0;
}