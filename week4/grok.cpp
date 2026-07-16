
#include <chrono>
#include <cstdio>
#include <cstdint>

double calculate(int64_t iterations, double param1, double param2) {
    double result = 1.0;
    for (int64_t i = 1; i <= iterations; ++i) {
        double j = i * param1 - param2;
        result -= 1.0 / j;
        j = i * param1 + param2;
        result += 1.0 / j;
    }
    return result;
}

int main() {
    auto start = std::chrono::high_resolution_clock::now();
    double result = calculate(200000000LL, 4.0, 1.0) * 4.0;
    auto end = std::chrono::high_resolution_clock::now();
    double elapsed = std::chrono::duration<double>(end - start).count();
    std::printf("Result: %.12f\n", result);
    std::printf("Execution Time: %.6f seconds\n", elapsed);
    return 0;
}
