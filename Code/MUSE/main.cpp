#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <conio.h>

#include "Filter.h"
#include "FIR_filter.h"
#include "PicometerController.h"


enum class MainStatus {
    IDLE,
    COLLECTING,
    SAVING,
    CONTINUOUS,
    STOPPING,
};

void collect_data(PicometerController& PC, FIRFilter& filter, std::vector<std::vector<float>>& raw, std::vector<std::vector<float>>& filtered) {
    if (PC.picometer_status == PicometerController::PicometerStatus::CONNECTED) {
        raw.emplace_back(PC.get_data().first);
        filtered.emplace_back(apply_filter(&filter, raw.back()));
    }
}

void write_data(PicometerController& PC, std::vector<std::vector<float>> raw, std::vector<std::vector<float>> filtered) {
    PC.write_data_to_csv(raw, "../Data/raw_sensor_data.csv");
    PC.write_data_to_csv(filtered, "../Data/filtered_data.csv");
}   

int main() {
    PicometerController PC;
    FIRFilter filter = {};

    MainStatus status = MainStatus::IDLE;
  
    unsigned int cutoff = 3;
    int column_index = 9;

    std::vector<std::vector<float>> result;
    std::vector<std::vector<float>> input_signal;

    std::vector<std::vector<float>> output_signal;

    filter_init(&filter);
    result.reserve(1000);
    input_signal.reserve(PC.get_data().first.size() - cutoff);
    output_signal.reserve(PC.get_data().first.size() - cutoff);
    bool print_start_info = true;

    ///*************************************************************** FOR CALCULATING SAMPLERATE ***************************************************************/
    //// Samplerate on Simons computer is: 17samples / 1.022seconds = 16.63 Hertz
    //// Get the current time
    //auto start_time = std::chrono::high_resolution_clock::now();

    //// Specify the duration you want the loop to run (1 second in this case)
    //std::chrono::milliseconds duration(1000);

    //while (true) {
    //    if (PC.picometer_status != PicometerController::PicometerStatus::CONNECTED) {
    //        break;
    //    }
    //    // Call get_data to retrieve impedance data for each time step
    //    auto impedanceData = PC.get_data().first;

    //    // Append the impedance data to the result vector
    //    result.emplace_back(impedanceData);

    //    // Get the current time again
    //    auto current_time = std::chrono::high_resolution_clock::now();

    //    // Calculate the elapsed time
    //    auto elapsed_time = std::chrono::duration_cast<std::chrono::milliseconds>(current_time - start_time);

    //    // Check if the desired duration has passed
    //    if (elapsed_time >= duration) {
    //        std::cout << "Loop completed after " << elapsed_time << " seconds." << std::endl;
    //        break; // Exit the loop after 1 second
    //    }
    //}
    //
    //for (auto i = 0; i < result.size(); i++)
    //    std::cout << result[i][0] << std::endl;
    ///*************************************************************** SAMPLERATE END ***************************************************************/

    while (true) {
        switch (status) {
            case MainStatus::IDLE:
                // Check if a key has been pressed
                if (print_start_info) {
                    print_start_info = false;
                    std::cout << "\n\nPress s to start the program" << std::endl;
                    std::cout << "While collecting data, press k to stop collecting data, and save it" << std::endl;
                    std::cout << "Ctrl + C at any point to exit.\n" << std::endl;
                }
                if (_kbhit()) {
                    char key = _getch();
                    if (key == 's') {
                        std::cout << "Key Pressed: " << key << std::endl;
                        std::cout << "Starting..." << std::endl;

                        status = MainStatus::COLLECTING;
                        break;
                    }
                }
                break;

            case MainStatus::COLLECTING:
                collect_data(PC, filter, input_signal, output_signal);
                // Check if a key has been pressed
                if (_kbhit()) {
                    char key = _getch();
                    if (key == 'k') {
                        std::cout << "Key Pressed: " << key << std::endl;
                        std::cout << "Stopping..." << std::endl;

                        status = MainStatus::SAVING;
                        break;
                    }
                }
                break;

            case MainStatus::SAVING:
                write_data(PC, input_signal, output_signal);
                status = MainStatus::STOPPING;
                break;

            case MainStatus::CONTINUOUS:
                write_data(PC, input_signal, output_signal);
                status = MainStatus::SAVING;
                break;

            case MainStatus::STOPPING:
                std::cout << "Data gathered and saved, stopping..." << std::endl;
                print_start_info = true;
                input_signal.clear();
                input_signal.reserve(PC.get_data().first.size() - cutoff);
                output_signal.clear();
                output_signal.reserve(PC.get_data().first.size() - cutoff);
                status = MainStatus::IDLE;
				break;
            
            default:
                status = MainStatus::IDLE;
                break;
            }
        }
    }