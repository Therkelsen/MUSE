#ifndef UTILS_H
#define UTILS_H

#include <chrono>
#include <cmath>
#include <ctime>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <utility>

namespace utils {
	/**
	* @brief Main states
	*/
	enum class MainStatus {
		IDLE,
		OFFLINE_MODE,
		COLLECTING,
		SAVING,
		CONTINUOUS,
		STOPPING,
	};

	/**
	* @brief Check if a file exists
	* @param path The path to the file
	* @return True if the file exists, false otherwise
	*/
	bool file_exists(const std::string& path) {
		std::ifstream file(path);
		return file.good();
	}

	/**
	* @brief Write data to a CSV file along a specific column, given by the index.
	*
	* This function writes data to a CSV file, appending the provided vectors of magnitude,
	* phase, and time to the specified file path. The data is written down a column specified
	* by the `column_index`. Additionally, an index column may be added, and the existing file
	* can be deleted before writing if specified.
	*
	* @param mag The vector of magnitudes to write to the CSV file.
	* @param phase The vector of phases to write to the CSV file.
	* @param time The vector of time values to write to the CSV file.
	* @param path The path to the CSV file.
	* @param delete_existing Whether to delete the existing file before writing.
	*
	* @note The vectors `mag`, `phase`, and `time` must have the same size.
	*/
	void write_data_to_csv(const std::vector<float>& mag, const std::vector<float>& phase, const std::vector<std::time_t>& time, const std::string& path, bool delete_existing) {
		std::string header = "Sample,EIMMagnitude,EIMPhase,JointAngle,Mass,Time";
		int curr_sample_index = 1;
		int last_sample_index = 1;
		if (delete_existing && utils::file_exists(path)) {
			if (std::remove(path.c_str()) != 0) {
				std::perror("Error deleting the existing file");
				return;
			} else {
				std::cout << "Existing file deleted" << std::endl;
			}
		} else {
			header = "";
			std::ifstream i_file(path);
			if (!i_file.is_open()) {
				std::cerr << "Failed to open the i_file: " << path << std::endl;
				return;
			}
			std::string skip_header;
			std::string line;
			if (std::getline(i_file, skip_header)) {
				while (std::getline(i_file, line)) {
					std::istringstream ss(line);
					std::string cell;

					if (std::getline(ss, cell, ',')) {
						curr_sample_index = std::stoi(cell) + 1;
						last_sample_index = curr_sample_index;
					}
				}
			} else {
				std::cerr << "Error reading the header line." << std::endl;
			}
		}

		if (curr_sample_index > 1) {
			std::cout << "Sample: " << curr_sample_index << std::endl;
		}

		std::ofstream o_file(path, std::ios::app);
		if (!o_file.is_open()) {
			std::cerr << "Failed to open the o_file: " << path << std::endl;
			return;
		}

		if (header != "") {
			o_file << header;
		}

		size_t data_size = 0;
		if (mag.size() >= phase.size()) {
			data_size = phase.size();
		} else if (mag.size() < phase.size()) {
			data_size = mag.size();
		} else {
			std::cerr << "Error: Data size is 0" << std::endl;
			o_file.close();
			return;
		}
		for (size_t i = 0; i < data_size; ++i) {
			o_file << "\n" << last_sample_index << "," << mag[i] << "," << phase[i] << ",0,0," << time[i];
		}

		o_file.close();
		std::cout << "Data has been written to " << path << std::endl;
	}

	/**
	* @brief Load filter coefficients from a CSV file
	*
	* @param coefficients_file The path to the file
	* @return A vector of vectors containing the filter coefficients
	*/
	std::vector<float> get_filter_coefficients(const std::string& coefficients_file) {
		if (!utils::file_exists(coefficients_file)) {
			throw std::runtime_error("Error loading file: " + coefficients_file + "\nExiting...");
			return {};
		}

		std::ifstream file(coefficients_file);
		if (!file.is_open()) {
			throw std::runtime_error("Failed to open the file: " + coefficients_file + "\nExiting...");
			return {};
		}

		std::string line;
		std::vector<float> filter_coefficients;

		while (std::getline(file, line)) {
			std::istringstream ss(line);
			std::string cell;

			while (std::getline(ss, cell, ',')) {
				try {
					float value = std::stof(cell);
					filter_coefficients.push_back(value);
				} catch (const std::invalid_argument& e) {
					std::cerr << "Error converting data: " << e.what() << std::endl;
					continue;
				}
			}
		}

		file.close();
		return filter_coefficients;
	}

	/**
	* @brief Collect data from the Picometer, apply a filter, and return both raw and filtered data.
	*
	* This function collects data from a PicometerController object, applies a Finite Impulse Response (FIR) filter
	* specified by the FIRFilter object, and returns both the raw and filtered data. The input signal is obtained from
	* the Picometer, and the modulus, phase, and time components are extracted and stored in the provided vectors.
	*
	* @param PC The PicometerController object providing the input signal.
	* @param filter The FIRFilter object used to filter the input signal.
	* @param modulus_input_signal Vector to store the raw modulus data.
	* @param phase_input_signal Vector to store the raw phase data.
	* @param time Vector to store the time data corresponding to the collected samples.
	*
	* @note The Picometer must be in a connected state (PicometerStatus::CONNECTED) for data collection to occur.
	*/
	void collect_data(PicometerController& PC, FIRFilter filter, std::vector<float>& modulus_input_signal, std::vector<float>& phase_input_signal, std::vector<std::time_t>& time) {
		if (PC.picometer_status == PicometerController::PicometerStatus::CONNECTED) {
			std::vector<float> modulus_input_row = PC.get_data().first;
			std::vector<float> phase_input_row = PC.get_data().second;

			modulus_input_signal.emplace_back(modulus_input_row[9]);
			phase_input_signal.emplace_back(abs(phase_input_row[9]));
			time.emplace_back(std::chrono::system_clock::to_time_t(std::chrono::system_clock::now()));
			return;
		}
		std::cout << "Error: Picometer not connected" << std::endl;
	}

	/**
	* @brief Collect data from a CSV file, apply a filter, and store both raw and filtered data.
	*
	* This function reads data from a CSV file specified by the input file path, extracts modulus,
	* phase, and time components, and stores the raw data in the provided vectors `mod`, `phase`,
	* and `time`. It then applies a Finite Impulse Response (FIR) filter to the modulus and phase
	* data and stores the filtered results in the vectors `filt_mod` and `filt_phase`.
	*
	* @param filter The FIRFilter object used to filter the input data.
	* @param input_file The path to the input CSV file.
	* @param mod Vector to store the raw modulus data.
	* @param phase Vector to store the raw phase data.
	* @param time Vector to store the time data corresponding to the collected samples.
	* @param filt_mod Vector to store the filtered modulus data.
	* @param filt_phase Vector to store the filtered phase data.
	*
	* @throws std::runtime_error If there is an error loading or processing the input file.
	*/
	void collect_data_from_file(FIRFilter& filter, const std::string& input_file, std::vector<float>& mod, std::vector<float>& phase, std::vector<std::time_t>& time,std::vector<float>& filt_mod, std::vector<float>& filt_phase) {
		if (!utils::file_exists(input_file)) {
			throw std::runtime_error("File: " + input_file + " does not exist\nExiting...");
		}

		std::ifstream file(input_file);
		if (!file.is_open()) {
			throw std::runtime_error("Error loading file: " + input_file + "\nExiting...");
		}

		std::string line;
		bool isHeader = true;
		while (std::getline(file, line)) {
			if (isHeader) {
				isHeader = false;
				continue;
			}

			std::istringstream ss(line);
			std::string cell;
			size_t col_idx = 0;
			float mod_value = 0.0f;
			float phase_value = 0.0f;
			time_t time_value = 0;

			while (std::getline(ss, cell, ',')) {
				try {
					float value = std::stof(cell);
					if (col_idx == 1) {
						mod_value = abs(value);
					} else if (col_idx == 2) {
						phase_value = abs(value);
					} else if (col_idx == 5) {
						time_value = value;
					}
				}
				catch (const std::invalid_argument& e) {
					std::cerr << "Error converting data: " << e.what() << std::endl;
					continue;
				}
				++col_idx;
			}

			mod.push_back(mod_value);
			phase.push_back(phase_value);
			time.push_back(time_value);
		}

		file.close();

		// Apply filter to mod and phase vectors once after collecting all data
		filt_mod = apply_filter(&filter, mod);
		filt_phase = apply_filter(&filter, phase);
	}
}
#endif // UTILS_H

