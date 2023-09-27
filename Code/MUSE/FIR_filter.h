#ifndef FIR_FILTER_H
#define FIR_FILTER_H
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdint.h>
#include <string>
#include <vector>

typedef struct {
	std::vector<float> buf;
	uint8_t buf_index;
	std::vector<float> impulse_response;

	float out;
} FIRFilter;

void filter_init(FIRFilter* fir, const std::vector<float>& filter_coefficients);
float filter_update(FIRFilter* fir, float inp);
std::vector<float> apply_filter(FIRFilter* fir, std::vector<float> input_signal);

#endif