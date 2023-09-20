#include <iostream>
#include <vector>

#include "DataInterface.h"
#include "Filter.h"
#include "FIR_filter.h"
#include "PicometerController.h"

int main() {
    PicometerController PC;
    FIRFilter filter = {};
  
    filter_init(&filter);

    PC.set_raw_sensor_data(PC.get_n_data_steps(25));

    if (PC.raw_data_ready) {
        std::cout << "PicometerController: Raw signal print: " << std::endl;
        PC.print_data(PC.get_raw_sensor_data());
    } else {
        std::cout << "PicometerController: Raw data not ready to print" << std::endl;
    }

    std::vector<std::vector<float>> output_signal;
    output_signal.reserve(PC.get_raw_sensor_data().size());
    if (PC.raw_data_ready) {
        for (int i = 0; i < PC.get_raw_sensor_data().size(); i++) {
            output_signal.emplace_back(apply_filter(&filter, PC.get_raw_sensor_data()[i]));
        }
        PC.set_filtered_sensor_data(output_signal);
        std::cout << "PicometerController: Filtered signal print: " << std::endl;
        PC.print_data(PC.get_filtered_sensor_data());
    } else {
        std::cout << "PicometerController: Filtered data not ready to print" << std::endl;
    }
    PC.print_data(PC.get_filtered_sensor_data());
}