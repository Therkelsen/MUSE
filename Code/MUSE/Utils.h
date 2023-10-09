#ifndef UTILS_H
#define UTILS_H

#include <cmath>
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
	* @brief Write data to a CSV file down a specific column given by the index
	*
	* @param data The data to write
	* @param path The path to the file
	* @param column_index The index of the column to write the data
	* @param add_index Whether to add an index column to the CSV file
	* @param delete_existing Whether to delete the existing file before writing
	*/
	void write_data_to_csv(const std::vector<float>& data, const std::string& path, size_t column_index, bool delete_existing) {
		if (delete_existing && utils::file_exists(path)) {
			if (std::remove(path.c_str()) != 0) {
				std::perror("Error deleting the existing file");
				return;
			}
		}

		std::ofstream file(path);
		if (!file.is_open()) {
			std::cerr << "Failed to open the file: " << path << std::endl;
			return;
		}

		file << "\"data\"\n";

		size_t dataSize = data.size();
		for (size_t i = 0; i < dataSize; ++i) {
			file << data[i] << "\n";
		}

		file.close();
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
	* Collect data from the picometer and apply the filter to the input data, returning both the raw and filtered data
	*
	* @param PC The PicometerController object
	* @param filter The FIRFilter object
	* @param input_signal The input signal
	* @param output_signal The output signal
	* @return A pair containing the raw and filtered data
	*/
	std::pair<std::vector<float>, std::vector<float>> collect_data(PicometerController& PC, FIRFilter filter, std::vector<float>& modulus_input_signal, std::vector<float>& phase_input_signal) {
		if (PC.picometer_status == PicometerController::PicometerStatus::CONNECTED) {
			std::vector<float> modulus_input_row = PC.get_data().first;
			std::vector<float> phase_input_row = PC.get_data().second;

			modulus_input_signal.emplace_back(modulus_input_row[9]);
			phase_input_signal.emplace_back(abs(phase_input_row[9]));

			return { modulus_input_signal, phase_input_signal };
		}
		std::cout << "Error: Picometer not connected" << std::endl;
		return { modulus_input_signal, phase_input_signal };  // Return the unchanged signals if not connected
	}

	/**
	* @brief Collect data from a file and apply the filter to the input data, storing both raw and filtered data
	*
	* @param filter The FIRFilter object
	* @param input_file The path to the input file
	* @param raw The raw data
	* @param filtered The filtered data
	*/
	void collect_data_from_file(FIRFilter& filter, const std::string& input_file, std::vector<float>& raw, std::vector<float>& filtered) {
		if (!utils::file_exists(input_file)) {
			throw std::runtime_error("Error loading file: " + input_file + "\nExiting...");
		}

		std::ifstream file(input_file);
		if (!file.is_open()) {
			throw std::runtime_error("Error loading file: " + input_file + "\nExiting...");
		}

		std::string line;
		raw.clear();
		filtered.clear();

		bool isHeader = true;
		while (std::getline(file, line)) {
			if (isHeader) {
				isHeader = false;
				continue;
			}

			std::istringstream ss(line);
			std::string cell;

			while (std::getline(ss, cell, ',')) {
				try {
					float value = std::stof(cell);
					raw.push_back(abs(value));
				} catch (const std::invalid_argument& e) {
					std::cerr << "Error converting data: " << e.what() << std::endl;
					continue;
				}
			}
				
			filtered = apply_filter(&filter, raw); // Apply filter and store filtered value
		}

		file.close();
	}
}
#endif // UTILS_H

