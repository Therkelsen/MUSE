#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <conio.h>

#include "Filter.h"
#include "FIR_filter.h"
#include "PicometerController.h"


int main() {
    PicometerController PC;
    FIRFilter filter = {};
  
    unsigned int cutoff = 3;
    int column_index = 9;
    filter_init(&filter);

    std::vector<std::vector<float>> result;
    result.reserve(1000);

    /*************************************************************** FOR CALCULATING SAMPLERATE ***************************************************************/
    // Samplerate on Simons computer is: 17samples / 1.022seconds = 16.63 Hertz
    // Get the current time
    auto start_time = std::chrono::high_resolution_clock::now();

    // Specify the duration you want the loop to run (1 second in this case)
    std::chrono::milliseconds duration(1000);

    while (true) {
        if (PC.picometer_status != PicometerController::PicometerStatus::CONNECTED) {
            break;
        }
        // Call get_data to retrieve impedance data for each time step
        auto impedanceData = PC.get_data().first;

        // Append the impedance data to the result vector
        result.emplace_back(impedanceData);

        // Get the current time again
        auto current_time = std::chrono::high_resolution_clock::now();

        // Calculate the elapsed time
        auto elapsed_time = std::chrono::duration_cast<std::chrono::milliseconds>(current_time - start_time);

        // Check if the desired duration has passed
        if (elapsed_time >= duration) {
            std::cout << "Loop completed after " << elapsed_time << " seconds." << std::endl;
            break; // Exit the loop after 1 second
        }
    }
    
    for (auto i = 0; i < result.size(); i++)
        std::cout << result[i][0] << std::endl;
    /*************************************************************** SAMPLERATE END ***************************************************************/

    //while (true) {
    //    PC.set_raw_sensor_data(PC.get_n_data_steps(25));

    //    //if (PC.raw_data_ready) {
    //    //    std::cout << "PicometerController: Raw signal print: " << std::endl;
    //    //    PC.print_data(PC.get_raw_sensor_data());
    //    //} else {
    //    //    std::cout << "PicometerController: Raw data not ready to print" << std::endl;
    //    //}

    //    std::vector<std::vector<float>> output_signal;
    //    output_signal.reserve(PC.get_raw_sensor_data().size() - cutoff);
    //    if (PC.raw_data_ready) {
    //        for (int i = cutoff; i < PC.get_raw_sensor_data().size(); i++) {
    //            output_signal.emplace_back(apply_filter(&filter, PC.get_raw_sensor_data()[i]));
    //        }
    //        //PC.set_filtered_sensor_data(output_signal);
    //        //std::cout << "PicometerController: Filtered signal print: " << std::endl;
    //        //PC.print_data(PC.get_filtered_sensor_data());
    //    }
    //    else {
    //        std::cout << "PicometerController: Filtered data not ready to print" << std::endl;
    //    }

    //    std::vector<float> single_freq = PC.get_frequency_column(output_signal, column_index);

    //    std::cout << std::endl << "The column at position " << column_index + 1 << " is:" << std::endl;
    //    for (size_t i = 0; i < single_freq.size(); i++) {
    //        std::cout << single_freq[i] << std::endl;
    //    }

    //    std::this_thread::sleep_for(std::chrono::seconds(1));

    //    // Check if a key has been pressed
    //    if (_kbhit()) {
    //        // Read the key (Windows-specific)
    //        char key = _getch();
    //        std::cout << "Key Pressed: " << key << std::endl;

    //        // Exit the loop if a key is pressed
    //        break;
    //    }
    //}
}