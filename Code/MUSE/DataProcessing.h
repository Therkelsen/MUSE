#ifndef DATA_PROCESSING_H
#define DATA_PROCESSING_H

#include <cmath>;
#include <vector>;

namespace data_processing {
    std::vector<std::vector<float>> rolling_mean(const std::vector<std::vector<float>>& input_signal) {
        std::vector<std::vector<float>> output_signal = input_signal;
        size_t buffer = input_signal.size() / 5;

        // Calculate running sum for the first buffer elements
        std::vector<float> running_sum(input_signal[0].size(), 0.0f);
        for (size_t i = 0; i < buffer; ++i) {
            for (size_t j = 0; j < input_signal[i].size(); ++j) {
                running_sum[j] += input_signal[i][j];
                output_signal[i][j] = running_sum[j] / static_cast<float>(i + 1);
            }
        }

        // Update running sum using sliding window approach for the rest of the elements
        for (size_t i = buffer; i < input_signal.size(); ++i) {
            for (size_t j = 0; j < input_signal[i].size(); ++j) {
                running_sum[j] = running_sum[j] + input_signal[i][j] - input_signal[i - buffer][j];
                output_signal[i][j] = running_sum[j] / static_cast<float>(buffer);
            }
        }

        return output_signal;
    }

    std::vector<std::vector<float>> cut_extremities(const std::vector<std::vector<float>>& input_signal, unsigned int std_dev) {
        std::vector<std::vector<float>> output_signal = input_signal;

        // Calculate mean and standard deviation for each column in the input signal
        std::vector<float> mean(input_signal[0].size(), 0.0f);
        std::vector<float> stddev(input_signal[0].size(), 0.0f);
        for (const auto& row : input_signal) {
            for (size_t j = 0; j < row.size(); ++j) {
                mean[j] += row[j];
            }
        }
        for (size_t j = 0; j < mean.size(); ++j) {
            mean[j] /= static_cast<float>(input_signal.size());
        }
        for (const auto& row : input_signal) {
            for (size_t j = 0; j < row.size(); ++j) {
                stddev[j] += std::pow(row[j] - mean[j], 2);
            }
        }
        for (size_t j = 0; j < stddev.size(); ++j) {
            stddev[j] = std::sqrt(stddev[j] / static_cast<float>(input_signal.size()));
        }

        // Cut off values that exceed the threshold
        for (size_t i = 0; i < input_signal.size(); ++i) {
            for (size_t j = 0; j < input_signal[i].size(); ++j) {
                float deviation = std::abs(input_signal[i][j] - mean[j]) / stddev[j];
                if (deviation > static_cast<float>(std_dev)) {
                    // Replace extreme values with the mean
                    output_signal[i][j] = mean[j];
                }
            }
        }

        return output_signal;
    }

};

#endif // DATA_PROCESSING_H