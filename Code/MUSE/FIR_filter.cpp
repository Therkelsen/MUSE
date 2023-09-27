#include "FIR_filter.h"

void filter_init(FIRFilter* fir, const std::vector<float>& filter_coefficients) {
	/* Initialize buf with zeros */
	fir->buf.assign(filter_coefficients.size(), 0.0f);

	/* Initialize impulse_response with filter_coefficients */
	fir->impulse_response = filter_coefficients;

	/* Reset buffer index */
	fir->buf_index = 0;

	/* Clear filter output */
	fir->out = 0.0f;
}

/* Follows the math of the convolution operation:
		y[n] = sum(j=0 to n-1)(h[j]*x[n-j])

		Where y is the output, h is the impulse response, n is the length of the impulse response
		x[n-j] is the shifted samples of our input buffer of our circular buffer
*/

float filter_update(FIRFilter* fir, float inp) {

	/* Stores latest sample buffer */
	fir->buf[fir->buf_index] = inp;

	/* Increments buffer index and wraps around if necessary */
	fir->buf_index++;

	if (fir->buf_index == fir->impulse_response.size()) {
		fir->buf_index = 0;
	}

	/* Compute new output sample (via convolution) */
	fir->out = 0.0f;

	uint8_t sumIndex = fir->buf_index;

	for (uint8_t n = 0; n < fir->impulse_response.size(); n++) {

		/* Decrements buffer index and wraps around if necessary */
		if (sumIndex > 0) {
			sumIndex--;
		}
		else {
			sumIndex = fir->impulse_response.size() - 1;
		}

		/* Multiply impulse response with shifted input sample and add to output */
		fir->out += fir->impulse_response[n] * fir->buf[sumIndex];
	}

	/* Return filter output */
	return fir->out;
}

std::vector<float> apply_filter(FIRFilter* fir, std::vector<float> input_signal) {
	std::vector<float> output_signal;
	output_signal.reserve(input_signal.size());
	for (unsigned int i = 0; i < input_signal.size(); i++) {
		output_signal.emplace_back(filter_update(fir, input_signal[i]));
	}
	return output_signal;
}