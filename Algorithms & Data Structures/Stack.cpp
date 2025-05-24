#include <iostream>

using namespace std;

#define MAX_SIZE 100  // Define the maximum size of the stack

class Stack {
private:
    int S[MAX_SIZE];  // Fixed-size array to store stack elements
    int top;          // Variable to track the top of the stack

public:
    Stack() {
        top = 0;  // Initialize the stack to be empty
    }

    // Function to check if the stack is empty
    bool StackEmpty() {
        if (top == 0) {
            return true;
        }
        return false;
    }

    // Function to push an element onto the stack
    void Push(int x) {
        if (top == MAX_SIZE) {
            cout << "Error: Overflow" << endl;
            // Alternatively, it can be written:
            // throw std::overflow_error("Stack overflow");
            return;
        } else {
            top = top + 1;
            S[top] = x;
        }
    }

    // Function to pop an element from the stack
    int Pop() {
        if (StackEmpty()) {
            cout << "Error: Underflow" << endl;
            // Alternatively, it can be written:
            // throw std::underflow_error("Stack underflow");
            return -1;  // Return a sentinel value for underflow
        } else {
            top = top - 1;
            return S[top + 1];
        }
    }

    // Function to display the stack elements
    void PrintStack() {
        if (StackEmpty()) {
            cout << "Stack is empty." << endl;
            return;
        }
        for (int i = 1; i <= top; i++) {
            cout << S[i] << " ";
        }
        cout << endl;
    }
};

int main() {
    Stack stack;

    // Test the push operation
    stack.Push(15);
    stack.Push(6);
    stack.Push(2);
    stack.Push(9);

    cout << "Original Stack: ";
    stack.PrintStack();

    // Push additional elements
    stack.Push(17);
    stack.Push(3);
    cout << "Stack after Push operations: ";
    stack.PrintStack();

    // Pop an element
    stack.Pop();
    cout << "Stack after Pop operation: ";
    stack.PrintStack();

    return 0;
}

//If You Want to Use Exceptions Instead of Printing Errors

// void Push(int x) {
//     if (top == MAX_SIZE) {
//         throw std::overflow_error("Stack overflow");
//     }
//     S[++top] = x;
// }

// int Pop() {
//     if (StackEmpty()) {
//         throw std::underflow_error("Stack underflow");
//     }
//     return S[top--];
// }

// int main() {
//     Stack stack;

//     try {
//         stack.Push(15);
//         stack.Push(6);
//         stack.Push(2);
//         stack.Push(9);

//         cout << "Original Stack: ";
//         stack.PrintStack();

//         stack.Push(17);
//         stack.Push(3);
//         cout << "Stack after Push operations: ";
//         stack.PrintStack();

//         stack.Pop();
//         cout << "Stack after Pop operation: ";
//         stack.PrintStack();

//     } catch (const std::overflow_error &e) {
//         cout << "Exception caught: " << e.what() << endl;
//     } catch (const std::underflow_error &e) {
//         cout << "Exception caught: " << e.what() << endl;
//     }

//     return 0;
// }