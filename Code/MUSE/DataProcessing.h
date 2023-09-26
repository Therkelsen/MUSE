#pragma once
#ifndef DATA_PROCESSING_H
#define DATA_PROCESSING_H

#include <vector>;

class DataProcessing {
public:
	DataProcessing() = default;
	int determine_intent(const std::vector<float> &data);

private:
	float sample_rate_ = 16.63;
	float samples_pr_second_ = 0.06;
};

#endif // DATA_PROCESSING_H