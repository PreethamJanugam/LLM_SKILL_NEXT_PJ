
#include <iostream>
#include <chrono>

double calculate(long long iterations, double param1, double param2) {
    double result = 1.0;
    long long i = 1;
    
    // Process in blocks of 16 to allow vectorized division and deep pipelining
    for (; i <= iterations - 15; i += 16) {
        double j1[16];
        double j2[16];
        double inv_j1[16];
        double inv_j2[16];
        
        #pragma clang loop vectorize(enable) interleave(enable)
        for (int k = 0; k < 16; ++k) {
            double current_i = static_cast<double>(i + k);
            j1[k] = current_i * param1 - param2;
            j2[k] = current_i * param1 + param2;
        }
        
        #pragma clang loop vectorize(enable) interleave(enable)
        for (int k = 0; k < 16; ++k) {
            inv_j1[k] = 1.0 / j1[k];
            inv_j2[k] = 1.0 / j2[k];
        }
        
        // Accumulate sequentially to rigidly preserve floating-point exactness
        for (int k = 0; k < 16; ++k) {
            result -= inv_j1[k];
            result += inv_j2[k];
        }
    }
    
    // Remaining iterations
    for (; i <= iterations; ++i) {
        double current_i = static_cast<double>(i);
        result -= 1.0 / (current_i * param1 - param2);
        result += 1.0 / (current_i * param1 + param2);
    }
    
    return result;
}

int main() {
    auto start_time = std::chrono::high_resolution_clock::now();
    
    double result = calculate(200000000, 4.0, 1.0) * 4.0;
    
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> execution_time = end_time - start_time;
    
    printf("Result: %.12f\n", result);
    printf("Execution Time: %.6f seconds\n", execution_time.count());
    
    return 0;
}
