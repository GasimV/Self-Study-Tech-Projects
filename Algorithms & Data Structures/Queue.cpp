#include <iostream>

using namespace std;

class Queue {
private:
    int Q[100];   // Fixed-size array for queue
    int head;     // Points to the front of the queue
    int tail;     // Points to the next insertion position
    int size;     // Maximum queue size

public:
    // Constructor to initialize the queue
    Queue(int s = 100) {
        size = s;
        head = 0;
        tail = 0;
    }

    // Function to check if the queue is empty
    bool isEmpty() {
        return head == tail;
    }

    // Function to check if the queue is full
    bool isFull() {
        return ((tail + 1) % size) == head;
    }

    // Enqueue operation
    void Enqueue(int x) {
        if (isFull()) {
            cout << "Queue Overflow!" << endl;
            return;
        }
        Q[tail] = x; // Store x at tail position
        if (tail == size)
            tail = 1; // Wrap around
        else
            tail = tail + 1;
    }

    // Dequeue operation
    int Dequeue() {
        if (isEmpty()) {
            cout << "Queue Underflow!" << endl;
            return -1; // Sentinel value for underflow
        }
        int x = Q[head]; // Retrieve value at head
        if (head == size) {
            head = 1;
        } else {
            head = head + 1;
        }
        return x;
    }

    // Print the queue
    void PrintQueue() {
        if (isEmpty()) {
            cout << "Queue is empty." << endl;
            return;
        }
        int i = head;
        while (i != tail) {
            cout << Q[i] << " ";
            if (i == size) {
                i = 1;
            } else {
                i++;
            }
        }
        cout << endl;
    }
};

// Main function for testing
int main() {
    Queue q(12); // Queue size of 12

    // Manually setting up the initial queue state
    q.Enqueue(15);
    q.Enqueue(6);
    q.Enqueue(9);
    q.Enqueue(8);
    q.Enqueue(4);

    cout << "Initial Queue: ";
    q.PrintQueue();

    // Performing Enqueue operations
    q.Enqueue(17);
    q.Enqueue(3);
    q.Enqueue(5);

    cout << "Queue after Enqueue() operation(s): ";
    q.PrintQueue();

    // Performing Dequeue operation
    int removed = q.Dequeue();
    cout << "Dequeued element: " << removed << endl;

    cout << "Queue after Dequeue() operation(s): ";
    q.PrintQueue();

    return 0;
}