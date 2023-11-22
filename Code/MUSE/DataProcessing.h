#ifndef DATA_PROCESSING_H
#define DATA_PROCESSING_H

namespace data_processing {
    /**
    * @brief Calculates a faux rolling mean for the input signal
    *
    * For the first 'buffer' elements, the rolling mean is calculated normally.
    * For the rest of the elements, the rolling mean is calculated using a sliding window approach.
    *
    * @param input_signal The input signal (single column)
    * @return The rolling mean of the input signal
    */
    std::vector<float> rolling_mean(const std::vector<float>& input_signal) {
        std::vector<float> output_signal = input_signal;
        size_t buffer = input_signal.size() / 75;
        float running_sum = 0.0f;

        for (size_t i = 0; i < input_signal.size(); ++i) {
            running_sum += input_signal[i];

            if (i < buffer) {
                output_signal[i] = running_sum / static_cast<float>(i + 1);
            }
            else {
                running_sum -= input_signal[i - buffer];
                output_signal[i] = running_sum / static_cast<float>(buffer);
            }
        }

        return output_signal;
    }

    /**
    * @brief Cuts extremities from the input signal based on the passed amount of standard deviations that should be considered normal
    *
    * @param input_signal The input signal (single column)
    * @param std_dev The amount of standard deviations that should be considered normal
    * @return The input signal with the extremities cut off
    */
    std::vector<float> cut_extremities(const std::vector<float>& input_signal, unsigned int std_dev) {
        std::vector<float> output_signal = input_signal;
        float mean = 0.0f;
        float stddev = 0.0f;

        // Calculate mean
        for (float value : input_signal) {
            mean += value;
        }
        mean /= static_cast<float>(input_signal.size());

        // Calculate standard deviation
        for (float value : input_signal) {
            stddev += static_cast<float>(std::pow(value - mean, 2));
        }
        stddev = std::sqrt(stddev / static_cast<float>(input_signal.size()));

        // Cut extremities based on standard deviations
        for (size_t i = 0; i < input_signal.size(); ++i) {
            float deviation = std::abs(input_signal[i] - mean) / stddev;
            if (deviation > static_cast<float>(std_dev)) {
                output_signal[i] = mean;
            }
        }

        return output_signal;
    }
};

#endif // DATA_PROCESSING_H