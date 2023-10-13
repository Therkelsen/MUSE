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
	std::pair<std::vector<float>, std::vector<float>> data;
	std::vector<float> modulus_input_signal;
	std::vector<float> modulus_output_signal;
	std::vector<float> modulus_processed_signal;
	std::vector<float> phase_input_signal;
	std::vector<float> phase_output_signal;
	std::vector<float> phase_processed_signal;
	std::vector<float> filter_coefficients;

	// Paths to the input data and filter coefficients
	const std::string modulus_input_file = "../Data/modulus_input_data.csv";
	const std::string phase_input_file = "../Data/phase_input_data.csv";
	const std::string filter_coefficients_file = "../Data/filter_coefficients.csv";

	const std::string modulus_raw_output_file = "../Data/modulus_raw_output_data.csv";
	const std::string modulus_filtered_output_file = "../Data/modulus_filtered_output_data.csv";
	const std::string modulus_processed_output_file = "../Data/modulus_processed_output_data.csv";

	const std::string phase_raw_output_file = "../Data/phase_raw_output_data.csv";
	const std::string phase_filtered_output_file = "../Data/phase_filtered_output_data.csv";
	const std::string phase_processed_output_file = "../Data/phase_processed_output_data.csv";

	// User input variables
	std::string user_input_fresh_sample;
	bool delete_existing = false;
	int user_input_data_index;

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
			std::cout << "Reading modulus data from file..." << std::endl;
			utils::collect_data_from_file(filter, modulus_input_file, modulus_input_signal, modulus_output_signal);
			std::cout << "Processing modulus data..." << std::endl;
			modulus_output_signal = data_processing::cut_extremities(apply_filter(&filter, modulus_input_signal), std_dev);
			modulus_processed_signal = data_processing::rolling_mean(modulus_output_signal);

			std::cout << "Reading phase data from file..." << std::endl;
			utils::collect_data_from_file(filter, phase_input_file, phase_input_signal, phase_output_signal);
			std::cout << "Processing phase data..." << std::endl;
			phase_output_signal = data_processing::cut_extremities(apply_filter(&filter, phase_input_signal), std_dev);
			phase_processed_signal = data_processing::rolling_mean(phase_output_signal);
			status = utils::MainStatus::SAVING;
			break;

		/**
		* @brief Collecting state, collects data until user inputs the stop command (k). Goes to saving state after stop command.
		*/
		case utils::MainStatus::COLLECTING:
			if (PC == nullptr) {
				PC = new PicometerController();
			}
			data = utils::collect_data(*PC, filter, modulus_input_signal, phase_input_signal);

			modulus_input_signal = data.first;
			phase_input_signal = data.second;

			if (_kbhit()) {
				char key = _getch();
				if (key == 'k') {
					std::cout << "Key Pressed: " << key << std::endl;
					std::cout << "Stopping..." << std::endl;

					modulus_output_signal = data_processing::cut_extremities(apply_filter(&filter, modulus_input_signal), std_dev);
					modulus_processed_signal = data_processing::rolling_mean(modulus_output_signal);

					phase_output_signal = data_processing::cut_extremities(apply_filter(&filter, phase_input_signal), std_dev);
					phase_processed_signal = data_processing::rolling_mean(phase_output_signal);

					status = utils::MainStatus::SAVING;
					break;
				}
			}
			break;

		/**
		* @brief Saving state, writes the collected data to csv files, and goes to stopping state after saving.
		*/
		case utils::MainStatus::SAVING:
			std::cout << "Is this a fresh sample? Press y or n: ";
			std::cin >> user_input_fresh_sample;
			if (user_input_fresh_sample == "y") {
				user_input_data_index = 0;
				delete_existing = true;
			} else {
				std::cout << "Enter the data index to continue from: ";
				std::cin >> user_input_data_index;
			}

			utils::write_data_to_csv(modulus_input_signal, modulus_raw_output_file, user_input_data_index, delete_existing);
			utils::write_data_to_csv(modulus_output_signal, modulus_filtered_output_file, user_input_data_index, delete_existing);
			utils::write_data_to_csv(modulus_processed_signal, modulus_processed_output_file, user_input_data_index, delete_existing);

			utils::write_data_to_csv(phase_input_signal, phase_raw_output_file, user_input_data_index, delete_existing);
			utils::write_data_to_csv(phase_output_signal, phase_filtered_output_file, user_input_data_index, delete_existing);
			utils::write_data_to_csv(phase_processed_signal, phase_processed_output_file, user_input_data_index, delete_existing);
			status = utils::MainStatus::STOPPING;
			break;

		/**
		* @brief W.I.P. Idea: Continuous state, continuously collects data, and writes it to csv files using a sort of circular queue.
		*/
		case utils::MainStatus::CONTINUOUS:
			status = utils::MainStatus::SAVING;
			break;

		/**
		* @brief Stopping state, Resets program variables, and goes back to idle state.
		*/
		case utils::MainStatus::STOPPING:
			std::cout << "Data gathered and saved, stopping..." << std::endl;
			print_start_info = true;
			modulus_input_signal.clear();
			modulus_output_signal.clear();
			modulus_processed_signal.clear();
			phase_input_signal.clear();
			phase_output_signal.clear();
			phase_processed_signal.clear();
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