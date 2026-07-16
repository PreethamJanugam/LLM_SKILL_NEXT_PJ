#include <cstdio>
#include <cstdint>
#include <chrono>

int main() {
    using namespace std::chrono;

    const int64_t iterations = 200000000LL;
    const int64_t param1 = 4;
    const int64_t param2 = 1;

    auto start_time = high_resolution_clock::now();

    double result = 1.0;
    int64_t xi = param1;

    int64_t i = 1;
    int64_t limit = iterations - (iterations % 8);

    // Manual unroll by 8 to reduce loop overhead while preserving operation order
    for (; i <= limit; i += 8) {
        int64_t j1 = xi - param2; result -= 1.0 / static_cast<double>(j1);
        int64_t j2 = xi + param2; result += 1.0 / static_cast<double>(j2);
        xi += param1;

        j1 = xi - param2; result -= 1.0 / static_cast<double>(j1);
        j2 = xi + param2; result += 1.0 / static_cast<double>(j2);
        xi += param1;

        j1 = xi - param2; result -= 1.0 / static_cast<double>(j1);
        j2 = xi + param2; result += 1.0 / static_cast<double>(j2);
        xi += param1;

        j1 = xi - param2; result -= 1.0 / static_cast<double>(j1);
        j2 = xi + param2; result += 1.0 / static_cast<double>(j2);
        xi += param1;

        j1 = xi - param2; result -= 1.0 / static_cast<double>(j1);
        j2 = xi + param2; result += 1.0 / static_cast<double>(j2);
        xi += param1;

        j1 = xi - param2; result -= 1.0 / static_cast<double>(j1);
        j2 = xi + param2; result += 1.0 / static_cast<double>(j2);
        xi += param1;

        j1 = xi - param2; result -= 1.0 / static_cast<double>(j1);
        j2 = xi + param2; result += 1.0 / static_cast<double>(j2);
        xi += param1;

        j1 = xi - param2; result -= 1.0 / static_cast<double>(j1);
        j2 = xi + param2; result += 1.0 / static_cast<double>(j2);
        xi += param1;
    }

    for (; i <= iterations; ++i) {
        int64_t j1 = xi - param2; result -= 1.0 / static_cast<double>(j1);
        int64_t j2 = xi + param2; result += 1.0 / static_cast<double>(j2);
        xi += param1;
    }

    result *= 4.0;

    auto end_time = high_resolution_clock::now();
    double elapsed = duration<double>(end_time - start_time).count();

    std::printf("Result: %.12f\n", result);
    std::printf("Execution Time: %.6f seconds\n", elapsed);
    return 0;
}