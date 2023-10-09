#include "FIR_filter.h"

/**
* @brief Initializes the FIR filter structure
* 
* @param fir Pointer to the FIR filter structure
* @param filter_coefficients Pointer to the filter coefficients
*/
void filter_init(FIRFilter* fir, const std::vector<float>& filter_coefficients) {
	fir->buf.assign(filter_coefficients.size(), 0.0f);
	fir->impulse_response = filter_coefficients;
	fir->buf_index = 0;
	fir->out = 0.0f;
}

/* 
*/
/**
* @brief Updates the FIR filter output with the latest input sample and returns the output sample.
* 
* Follows the math of the convolution operation:
* y[n] = sum(j=0 to n-1)(h[j]*x[n-j])
* Where y is the output, h is the impulse response, n is the length of the impulse response
* x[n-j] is the shifted samples of our input buffer of our circular buffer
* 
* @param fir Pointer to the FIR filter structure
* @param inp The latest input sample
* @return The latest output sample
*/
float filter_update(FIRFilter* fir, float inp) {
	fir->buf[fir->buf_index] = inp;
	fir->buf_index++;

	if (fir->buf_index == fir->impulse_response.size()) {
		fir->buf_index = 0;
	}

	fir->out = 0.0f;

	uint8_t sumIndex = fir->buf_index;

	for (uint8_t n = 0; n < fir->impulse_response.size(); n++) {
		if (sumIndex > 0) {
			sumIndex--;
		} else {
			sumIndex = fir->impulse_response.size() - 1;
		}

		fir->out += fir->impulse_response[n] * fir->buf[sumIndex];
	}

	return fir->out;
}

/**
* @brief Applies the FIR filter to the input signal and returns the output signal.
* 
* @param fir Pointer to the FIR filter structure
* @param input_signal The input signal
* @return The output signal
*/
std::vector<float> apply_filter(FIRFilter* fir, const std::vector<float>& input_signal) {
	std::vector<float> output_signal;
	output_signal.reserve(input_signal.size());
	for (unsigned int i = 0; i < input_signal.size(); i++) {
		output_signal.emplace_back(filter_update(fir, input_signal[i]));
	}
	return output_signal;
}