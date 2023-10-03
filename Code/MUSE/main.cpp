#include <chrono>
#include <conio.h>
#include <fstream>
#include <iostream>
#include <sstream>
#include <thread>
#include <vector>

#include "DataProcessing.h"
#include "Filter.h"
#include "FIR_filter.h"
#include "PicometerController.h"
#include "Utils.h"

// declare uninitialized pointer to the picometercontroller, since running the constructor will crash if the device is not connected
PicometerController* PC;

int main() {
	FIRFilter filter = {};

	utils::MainStatus status = utils::MainStatus::IDLE;

	// Standard deviation for the extremity cutting
	unsigned int std_dev = 2;

	// Datatypes for sensor data and filter coefficients
	std::pair<std::vector<std::vector<float>>, std::vector<std::vector<float>>> data;
	std::vector<std::vector<float>> input_signal;
	std::vector<std::vector<float>> output_signal;
	std::vector<std::vector<float>> processed_signal;
	std::vector<float> filter_coefficients;

	// Paths to the input data and filter coefficients
	const std::string input_file = "../Data/input_data.csv";
	const std::string filter_coefficients_file = "../Data/filter_coefficients.csv";

	filter_init(&filter, utils::get_filter_coefficients(filter_coefficients_file));
	bool print_start_info = true;

	while (true) {
		switch (status) {
		/**
		* @brief Idle state, waiting for user input
		*/
		case utils::MainStatus::IDLE:
			if (print_start_info) {
				print_start_info = false;
				std::cout << "\n\nPress s to start the program" << std::endl;
				std::cout << "While collecting data, press k to stop collecting data, and save it" << std::endl;
				std::cout << "Press f to run in offline mode (Eliko device is not connected)" << std::endl;
				std::cout << "Ctrl + C at any point to exit.\n" << std::endl;
			}

			if (_kbhit()) {
				char key = _getch();
				std::cout << "Key Pressed: " << key << std::endl;
				if (key == 's') {
					std::cout << "Starting..." << std::endl;
					status = utils::MainStatus::COLLECTING;
					break;
				}

				if (key == 'f') {
					std::cout << "Starting in offline mode..." << std::endl;
					status = utils::MainStatus::OFFLINE_MODE;
					break;
				}
			}
			break;

		/**
		* @brief Offline mode state, reads and processes data from a file, in case the Eliko device is not connected. Goes to saving state after processing.
		*/
		case utils::MainStatus::OFFLINE_MODE:
			utils::collect_data_from_file(filter, input_file, input_signal, output_signal);
			processed_signal = data_processing::rolling_mean(output_signal);
			status = utils::MainStatus::SAVING;
			break;

		/**
		* @brief Collecting state, collects data until user inputs the stop command (k). Goes to saving state after stop command.
		*/
		case utils::MainStatus::COLLECTING:
			if (PC == nullptr) {
				PC = new PicometerController();
			}
			data = utils::collect_data(*PC, filter, input_signal, output_signal);
			input_signal = data.first;
			output_signal = data.second;
			processed_signal = data_processing::cut_extremities(output_signal, std_dev);
			processed_signal = data_processing::rolling_mean(processed_signal);
			if (_kbhit()) {
				char key = _getch();
				if (key == 'k') {
					std::cout << "Key Pressed: " << key << std::endl;
					std::cout << "Stopping..." << std::endl;

					status = utils::MainStatus::SAVING;
					break;
				}
			}
			break;

		/**
		* @brief Saving state, writes the collected data to csv files, and goes to stopping state after saving.
		*/
		case utils::MainStatus::SAVING:
			utils::write_data_to_csv(input_signal, "../Data/raw_sensor_data.csv");
			utils::write_data_to_csv(output_signal, "../Data/filtered_data.csv");
			utils::write_data_to_csv(processed_signal, "../Data/processed_data.csv");
			status = utils::MainStatus::STOPPING;
			break;

		/**
		* @brief W.I.P. Idea: Continuous state, continuously collects data, and writes it to csv files using a sort of circular queue.
		*/
		case utils::MainStatus::CONTINUOUS:
			utils::write_data_to_csv(input_signal, "../Data/raw_sensor_data.csv");
			utils::write_data_to_csv(output_signal, "../Data/filtered_data.csv");
			utils::write_data_to_csv(processed_signal, "../Data/processed_data.csv");
			status = utils::MainStatus::SAVING;
			break;

		/**
		* @brief Stopping state, Resets program variables, and goes back to idle state.
		*/
		case utils::MainStatus::STOPPING:
			std::cout << "Data gathered and saved, stopping..." << std::endl;
			print_start_info = true;
			input_signal.clear();
			output_signal.clear();
			processed_signal.clear();
			status = utils::MainStatus::IDLE;
			break;

		/**
		*	@brief Default case, should never be reached.
		*/
		default:
			std::cout << "Error: Invalid state reached, returning to Idle state" << std::endl;
			status = utils::MainStatus::IDLE;
			break;
		}
	}
	// Delete the picometercontroller object to prevent memory leaks
	delete PC;
}