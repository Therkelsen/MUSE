#ifndef FIR_FILTER_H
#define FIR_FILTER_H
#include <stdint.h>
#include <vector>

#define FIR_FILTER_LENGTH 4

typedef struct {
    float buf[FIR_FILTER_LENGTH];
    uint8_t bufIndex;

    float out;
} FIRFilter;

void filter_init(FIRFilter *fir);
float filter_update(FIRFilter *fir, float inp);
std::vector<float> apply_filter(FIRFilter* fir, std::vector<float> input_signal);

#endif