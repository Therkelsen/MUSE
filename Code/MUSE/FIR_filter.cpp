#include <stdint.h>
#include "FIR_filter.h"

// Array that will contain our impulse respons.
static float FIR_IMPULSE_RESPONSE[FIR_FILTER_LENGTH] = {
    0.11605495396712117717186174559174105525,
    0.392686976596185288723717121683876030147,
    0.392686976596185288723717121683876030147,
    0.11605495396712117717186174559174105525};

void filter_init(FIRFilter *fir) {

    /* Clear filter buffer */
    for(uint8_t n = 0; n < FIR_FILTER_LENGTH; n++) {
        fir->buf[n] = 0.0f;

    }

    /* Reset buffer index */
    fir->bufIndex = 0;

    /* Clear filter output */
    fir->out = 0.0f;
};

/* Follows the math of the convolution operation:
        y[n] = sum(j=0 to n-1)(h[j]*x[n-j])
        
        Where y is the output, h is the impulse response, n is the length of the impulse response
        x[n-j] is the shifted samples of our input buffer of our circular buffer
*/

float filter_update(FIRFilter *fir, float inp) {
    
    /* Stores latest sample buffer */
    fir->buf[fir->bufIndex] = inp;

    /* Increments buffer index and wraps around if necessary */
    fir->bufIndex++;

    if (fir->bufIndex == FIR_FILTER_LENGTH) {
        fir->bufIndex = 0;
    }

    /* Compute new output sample (via convolution) */
    fir->out = 0.0f;

    uint8_t sumIndex = fir->bufIndex;

    for(uint8_t n = 0; n < FIR_FILTER_LENGTH; n++) {

        /* Decrements buffer index and wraps around if necessary */
        if(sumIndex > 0) {
            sumIndex--;
        } else {
            sumIndex = FIR_FILTER_LENGTH-1;
        }

        /* Multiply impulse response with shifted input sample and add to output */
        fir->out += FIR_IMPULSE_RESPONSE[n] * fir->buf[sumIndex];
    }

    /* Return filter output */
    return fir->out;
}

std::vector<float> apply_filter(FIRFilter* fir, std::vector<float> input_signal) {
    std::vector<float> output_signal; 
    output_signal.reserve(input_signal.size());
    for(unsigned int i = 0; i < input_signal.size(); i++) {
		output_signal.emplace_back(filter_update(fir, input_signal[i]));
	}
    return output_signal;
}