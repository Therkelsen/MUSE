#include <stdint.h>
#include "FIR_filter.h"

// Array that will contain our impulse respons.
static float FIR_IMPULSE_RESPONSE[FIR_FILTER_LENGTH] = {
    -0.0096885631125593965617959213432186516,
    - 0.018288704022953281014274296012445120141,
    0.058878785660602249441009092834065086208,
    0.089240442198602568102394627658213721588,
    - 0.154440953757407795077227774527273140848,
    - 0.189740787364098023592973163431452121586,
    0.223994076947065801075353874693973921239,
    0.223994076947065801075353874693973921239,
    - 0.189740787364098023592973163431452121586,
    - 0.154440953757407795077227774527273140848,
    0.089240442198602568102394627658213721588,
    0.058878785660602249441009092834065086208,
    - 0.018288704022953281014274296012445120141,
    - 0.0096885631125593965617959213432186516};

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