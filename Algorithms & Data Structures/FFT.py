"""
Recursive Fast Fourier Transform (FFT)

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
       y[0] = 4 + 6 = 10
       y[1] = -2 + i(-2) = -2 - 2i
       y[2] = 4 - 6 = -2
       y[3] = -2 - i(-2) = -2 + 2i

Final result:
       FFT([1, 2, 3, 4]) = [10, -2 - 2i, -2, -2 + 2i]

Example program input (each value is a real/imaginary pair):
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

y[0] is the sum of the input values. The other results describe the
complex frequency components of the original sequence.
"""

import cmath
import math


def fft(a: list[complex]) -> list[complex]:
    """Return the recursive FFT of a power-of-two-length sequence."""
    n = len(a)

    # The DFT of one element is the element itself.
    if n == 1:
        return a.copy()

    if n == 0 or n & (n - 1):
        raise ValueError("FFT input size must be a power of two")

    omega_n = cmath.exp(2j * math.pi / n)
    omega = 1.0 + 0.0j

    a_even = a[0::2]
    a_odd = a[1::2]

    y_even = fft(a_even)
    y_odd = fft(a_odd)
    y = [0j] * n

    for k in range(n // 2):
        y[k] = y_even[k] + omega * y_odd[k]
        y[k + n // 2] = y_even[k] - omega * y_odd[k]
        omega *= omega_n

    return y


def format_complex(value: complex) -> str:
    """Format a complex number in the same style as the C++ program."""
    # Avoid displaying tiny floating-point errors as nonzero values.
    real = 0.0 if abs(value.real) < 1e-12 else value.real
    imaginary = 0.0 if abs(value.imag) < 1e-12 else value.imag
    sign = "-" if imaginary < 0 else "+"
    return f"{real:.6f} {sign} {abs(imaginary):.6f}i"


def main() -> None:
    try:
        n = int(input("Enter n (a power of two): "))
    except ValueError:
        print("Invalid input for n.")
        return

    values: list[complex] = []
    print(f"Enter {n} values as real imaginary pairs:")

    for index in range(n):
        try:
            parts = input().split()
            if len(parts) != 2:
                raise ValueError
            real_part, imaginary_part = map(float, parts)
        except ValueError:
            print(f"Invalid complex value at index {index}.")
            return

        values.append(complex(real_part, imaginary_part))

    try:
        result = fft(values)
    except ValueError as error:
        print(error)
        return

    for k, value in enumerate(result):
        print(f"y[{k}] = {format_complex(value)}")


if __name__ == "__main__":
    main()
