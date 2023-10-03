#ifndef UTILS_H
#define UTILS_H

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
	* @brief Write data to a CSV file
	* 
	* @param data The data to write
	* @param path The path to the file
	*/
	void write_data_to_csv(const std::vector<std::vector<float>>& data, const std::string& path) {
		if (utils::file_exists(path)) {
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

		file << "\"freq_1\", \"freq_2\", \"freq_3\", \"freq_4\", \"freq_5\", \"freq_6\", \"freq_7\", \"freq_8\", \"freq_9\", \"freq_10\", \"freq_11\", \"freq_12\", \"freq_13\", \"freq_14\", \"freq_15\"\n";

		for (const std::vector<float>& row : data) {
			for (size_t i = 0; i < row.size(); ++i) {
				file << row[i];
				if (i < row.size() - 1) {
					file << ",";
				}
			}
			file << "\n";
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
	std::pair<std::vector<std::vector<float>>, std::vector<std::vector<float>>> collect_data(PicometerController& PC, FIRFilter filter, std::vector<std::vector<float>>& input_signal, std::vector<std::vector<float>>& output_signal) {
		if (PC.picometer_status == PicometerController::PicometerStatus::CONNECTED) {
			std::vector<float> input_row;
			std::vector<float> output_row;

			// Collect data from the picometer
			input_row = PC.get_data().first;

			// Apply the filter to the input data
			output_row = apply_filter(&filter, input_row);

			// Append the collected data to input_signal and output_signal
			input_signal.emplace_back(input_row);
			output_signal.emplace_back(output_row);

			return { input_signal, output_signal };
		}
		return { input_signal, output_signal };  // Return the unchanged signals if not connected
	}

	/**
	* @brief Collect data from a file and apply the filter to the input data, returning both the raw and filtered data
	* 
	* @param filter The FIRFilter object
	* @param input_file The path to the input file
	* @param raw The raw data
	* @param filtered The filtered data
	*/
	void collect_data_from_file(FIRFilter& filter, const std::string& input_file, std::vector<std::vector<float>>& raw, std::vector<std::vector<float>>& filtered) {
		if (!utils::file_exists(input_file)) {
			throw std::runtime_error("Error loading file: " + input_file + "\nExiting...");
			return;
		}

		std::ifstream file(input_file);
		if (!file.is_open()) {
			throw std::runtime_error("Error loading file: " + input_file + "\nExiting...");
			return;
		}

		std::string line;
		raw.clear();

		bool isHeader = true;
		while (std::getline(file, line)) {
			if (isHeader) {
				isHeader = false;
				continue;
			}

			std::vector<float> row;
			std::istringstream ss(line);
			std::string cell;

			while (std::getline(ss, cell, ',')) {
				try {
					float value = std::stof(cell);
					row.push_back(value);
				}
				catch (const std::invalid_argument& e) {
					std::cerr << "Error converting data: " << e.what() << std::endl;
					continue;
				}
			}
			raw.emplace_back(row);
			filtered.emplace_back(apply_filter(&filter, row));
		}

		file.close();
	}
}
#endif // UTILS_H

