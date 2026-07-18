/*
Illustrative example
====================

Input sequence: a = [1, 2, 3, 4], where n = 4.

1. Split the sequence by index:
       a_even = [a[0], a[2]] = [1, 3]
       a_odd  = [a[1], a[3]] = [2, 4]

2. Recursively compute both two-element FFTs:
       FFT(a_even) = [1 + 3, 1 - 3] = [4, -2]
       FFT(a_odd)  = [2 + 4, 2 - 4] = [6, -2]

3. Combine them using omega_n = exp(2*pi*i/n).
   For n = 4, omega_n = i:
       k = 0, omega = 1:
           y[0] = 4 + 1(6) = 10
           y[2] = 4 - 1(6) = -2

       k = 1, omega = i:
           y[1] = -2 + i(-2) = -2 - 2i
           y[3] = -2 - i(-2) = -2 + 2i

Final result:
       FFT([1, 2, 3, 4]) = [10, -2 - 2i, -2, -2 + 2i]

Example program input (each value is entered as a real/imaginary pair):
       4
       1 0
       2 0
       3 0
       4 0

Program output:
       y[0] = 10.000000 + 0.000000i
       y[1] = -2.000000 - 2.000000i
       y[2] = -2.000000 + 0.000000i
       y[3] = -2.000000 + 2.000000i

Simple explanation of the output:
       y[0] is the sum of all input values: 1 + 2 + 3 + 4 = 10.
       y[1] and y[3] contain imaginary parts because the FFT represents
       the sequence using complex frequency components.
       y[2] is real and represents the alternating component of the input.
       Together, y[0] through y[3] are the frequency-domain form of the
       original sequence [1, 2, 3, 4].
*/

#include <cmath>
#include <complex>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>

using Complex = std::complex<double>;

std::vector<Complex> FFT(const std::vector<Complex>& a) {
    const std::size_t n = a.size();

    // The DFT of one element is the element itself.
    if (n == 1) {
        return a;
    }

    if (n == 0 || (n & (n - 1)) != 0) {
        throw std::invalid_argument("FFT input size must be a power of two");
    }

    const double pi = std::acos(-1.0);
    const Complex omega_n = std::polar(1.0, 2.0 * pi / n);
    Complex omega = 1.0;

    std::vector<Complex> a_even(n / 2);
    std::vector<Complex> a_odd(n / 2);

    for (std::size_t i = 0; i < n / 2; ++i) {
        a_even[i] = a[2 * i];
        a_odd[i] = a[2 * i + 1];
    }

    const std::vector<Complex> y_even = FFT(a_even);
    const std::vector<Complex> y_odd = FFT(a_odd);
    std::vector<Complex> y(n);

    for (std::size_t k = 0; k < n / 2; ++k) {
        y[k] = y_even[k] + omega * y_odd[k];
        y[k + n / 2] = y_even[k] - omega * y_odd[k];
        omega *= omega_n;
    }

    return y;
}

int main() {
    std::size_t n;
    std::cout << "Enter n (a power of two): ";
    if (!(std::cin >> n)) {
        std::cerr << "Invalid input for n.\n";
        return 1;
    }

    std::vector<Complex> a(n);
    std::cout << "Enter " << n << " values as real imaginary pairs:\n";

    for (std::size_t i = 0; i < n; ++i) {
        double real_part;
        double imaginary_part;

        if (!(std::cin >> real_part >> imaginary_part)) {
            std::cerr << "Invalid complex value at index " << i << ".\n";
            return 1;
        }

        a[i] = Complex(real_part, imaginary_part);
    }

    try {
        const std::vector<Complex> result = FFT(a);

        std::cout << std::fixed << std::setprecision(6);
        for (std::size_t k = 0; k < result.size(); ++k) {
            std::cout << "y[" << k << "] = " << result[k].real();
            std::cout << (result[k].imag() < 0 ? " - " : " + ")
                      << std::abs(result[k].imag()) << "i\n";
        }
    } catch (const std::invalid_argument& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }

    return 0;
}
